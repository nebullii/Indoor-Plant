#!/usr/bin/env bash
# ============================================================================
# Indoor Plant Platform - Google Cloud Deployment Script
# ============================================================================
# Usage:
#   ./deploy.sh               Full deployment (first time)
#   ./deploy.sh --update      Rebuild & redeploy app only
#   ./deploy.sh --secrets-only Update secrets from .env only
# ============================================================================
set -euo pipefail

# --- Configuration ---
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="us-central1"
SERVICE_NAME="indoor-plant"
DB_INSTANCE_NAME="indoor-plant-db"
DB_NAME="indoor_plant"
DB_USER="indoor_plant_user"
REPO_NAME="indoor-plant-repo"
BUCKET_NAME="${PROJECT_ID}-media"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# Secrets to sync from .env to Secret Manager
SECRETS_LIST=(
    SECRET_KEY
    STRIPE_PUBLIC_KEY
    STRIPE_SECRET_KEY
    OPENAI_API_KEY
    SENDGRID_API_KEY
    FEDEX_API_KEY
    FEDEX_API_SECRET
    FEDEX_ACCOUNT_NUMBER
    GITHUB_WEBHOOK_SECRET
)

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }
info()  { echo -e "${BLUE}[→]${NC} $1"; }

# --- Prerequisites Check ---
check_prerequisites() {
    info "Checking prerequisites..."

    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)
        if [ -z "$PROJECT_ID" ]; then
            error "No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
            error "Or set GCP_PROJECT_ID environment variable"
            exit 1
        fi
        BUCKET_NAME="${PROJECT_ID}-media"
        IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"
    fi

    if [ ! -f ".env" ]; then
        warn ".env not found. Skipping local secret sync; expecting Secret Manager to be pre-populated."
    fi

    log "Prerequisites OK (project: ${PROJECT_ID})"
}

# --- Enable APIs ---
enable_apis() {
    info "Enabling required GCP APIs..."
    gcloud services enable \
        run.googleapis.com \
        sqladmin.googleapis.com \
        artifactregistry.googleapis.com \
        secretmanager.googleapis.com \
        cloudbuild.googleapis.com \
        storage.googleapis.com \
        --project="${PROJECT_ID}" \
        --quiet
    log "APIs enabled"
}

# --- Artifact Registry ---
create_artifact_registry() {
    info "Creating Artifact Registry repository..."
    if gcloud artifacts repositories describe "${REPO_NAME}" \
        --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
        log "Artifact Registry repo already exists"
    else
        gcloud artifacts repositories create "${REPO_NAME}" \
            --repository-format=docker \
            --location="${REGION}" \
            --project="${PROJECT_ID}" \
            --quiet
        log "Artifact Registry repo created"
    fi
}

# --- Secrets ---
sync_secrets() {
    info "Syncing secrets from .env to Secret Manager..."

    # Load .env file
    set -a
    source .env
    set +a

    for secret_name in "${SECRETS_LIST[@]}"; do
        local secret_value="${!secret_name:-}"
        if [ -z "$secret_value" ]; then
            warn "Skipping ${secret_name} (not set in .env)"
            continue
        fi

        # Create or update secret
        if gcloud secrets describe "${secret_name}" --project="${PROJECT_ID}" &>/dev/null; then
            echo -n "${secret_value}" | gcloud secrets versions add "${secret_name}" \
                --data-file=- --project="${PROJECT_ID}" --quiet
            log "Updated secret: ${secret_name}"
        else
            echo -n "${secret_value}" | gcloud secrets create "${secret_name}" \
                --data-file=- --replication-policy="automatic" \
                --project="${PROJECT_ID}" --quiet
            log "Created secret: ${secret_name}"
        fi
    done
}

# --- Database ---
create_database() {
    info "Setting up Cloud SQL PostgreSQL instance..."

    # Check if instance exists
    if gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" &>/dev/null; then
        log "Cloud SQL instance already exists"
    else
        info "Creating Cloud SQL instance (this takes 5-10 minutes)..."
        gcloud sql instances create "${DB_INSTANCE_NAME}" \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region="${REGION}" \
            --storage-type=HDD \
            --storage-size=10GB \
            --project="${PROJECT_ID}" \
            --quiet
        log "Cloud SQL instance created"
    fi

    # Generate DB password
    local db_password
    db_password=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)

    # Set DB user password
    if gcloud sql users describe "${DB_USER}" \
        --instance="${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" &>/dev/null; then
        gcloud sql users set-password "${DB_USER}" \
            --instance="${DB_INSTANCE_NAME}" \
            --password="${db_password}" \
            --project="${PROJECT_ID}" \
            --quiet
        log "Updated DB user password"
    else
        gcloud sql users create "${DB_USER}" \
            --instance="${DB_INSTANCE_NAME}" \
            --password="${db_password}" \
            --project="${PROJECT_ID}" \
            --quiet
        log "Created DB user: ${DB_USER}"
    fi

    # Create database
    if gcloud sql databases describe "${DB_NAME}" \
        --instance="${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" &>/dev/null; then
        log "Database '${DB_NAME}' already exists"
    else
        gcloud sql databases create "${DB_NAME}" \
            --instance="${DB_INSTANCE_NAME}" \
            --project="${PROJECT_ID}" \
            --quiet
        log "Database '${DB_NAME}' created"
    fi

    # Store DB password in Secret Manager
    if gcloud secrets describe DATABASE_PASSWORD --project="${PROJECT_ID}" &>/dev/null; then
        echo -n "${db_password}" | gcloud secrets versions add DATABASE_PASSWORD \
            --data-file=- --project="${PROJECT_ID}" --quiet
    else
        echo -n "${db_password}" | gcloud secrets create DATABASE_PASSWORD \
            --data-file=- --replication-policy="automatic" \
            --project="${PROJECT_ID}" --quiet
    fi
    log "DB password stored in Secret Manager"

    # Build DATABASE_URL and store it
    local connection_name
    connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" --format='value(connectionName)')
    local database_url="postgres://${DB_USER}:${db_password}@//cloudsql/${connection_name}/${DB_NAME}"

    if gcloud secrets describe DATABASE_URL --project="${PROJECT_ID}" &>/dev/null; then
        echo -n "${database_url}" | gcloud secrets versions add DATABASE_URL \
            --data-file=- --project="${PROJECT_ID}" --quiet
    else
        echo -n "${database_url}" | gcloud secrets create DATABASE_URL \
            --data-file=- --replication-policy="automatic" \
            --project="${PROJECT_ID}" --quiet
    fi
    log "DATABASE_URL stored in Secret Manager"

    # Generate and store superuser password
    local superuser_password
    superuser_password=$(openssl rand -base64 18 | tr -d '/+=' | head -c 16)

    if gcloud secrets describe DJANGO_SUPERUSER_PASSWORD --project="${PROJECT_ID}" &>/dev/null; then
        echo -n "${superuser_password}" | gcloud secrets versions add DJANGO_SUPERUSER_PASSWORD \
            --data-file=- --project="${PROJECT_ID}" --quiet
    else
        echo -n "${superuser_password}" | gcloud secrets create DJANGO_SUPERUSER_PASSWORD \
            --data-file=- --replication-policy="automatic" \
            --project="${PROJECT_ID}" --quiet
    fi
    log "Superuser password stored in Secret Manager"
}

# --- Cloud Storage ---
create_storage_bucket() {
    info "Setting up Cloud Storage bucket for media files..."

    if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
        log "Storage bucket already exists"
    else
        gcloud storage buckets create "gs://${BUCKET_NAME}" \
            --location="${REGION}" \
            --project="${PROJECT_ID}" \
            --uniform-bucket-level-access \
            --quiet
        log "Storage bucket created: gs://${BUCKET_NAME}"
    fi

    # Set public read access for media files
    gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
        --member="allUsers" \
        --role="roles/storage.objectViewer" \
        --project="${PROJECT_ID}" \
        --quiet 2>/dev/null || true
    log "Bucket configured for public read access"
}

# --- IAM ---
setup_iam() {
    info "Configuring IAM roles for Cloud Run service account..."

    local project_number
    project_number=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
    local sa="${project_number}-compute@developer.gserviceaccount.com"

    # Secret Manager access
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${sa}" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet &>/dev/null
    log "Granted secretmanager.secretAccessor"

    # Cloud SQL client
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${sa}" \
        --role="roles/cloudsql.client" \
        --quiet &>/dev/null
    log "Granted cloudsql.client"

    # Storage admin for media uploads
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${sa}" \
        --role="roles/storage.objectAdmin" \
        --quiet &>/dev/null
    log "Granted storage.objectAdmin"
}

# --- Build & Deploy ---
build_and_deploy() {
    info "Building container image via Cloud Build..."
    gcloud builds submit \
        --tag="${IMAGE_URI}" \
        --project="${PROJECT_ID}" \
        --quiet
    log "Container image built and pushed"

    # Get Cloud SQL connection name
    local connection_name
    connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" --format='value(connectionName)')

    info "Deploying to Cloud Run..."
    gcloud run deploy "${SERVICE_NAME}" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --platform=managed \
        --allow-unauthenticated \
        --port=8080 \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=3 \
        --set-env-vars="USE_HTTPS=True,USE_GCS=True,GCS_BUCKET_NAME=${BUCKET_NAME}" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
OPENAI_API_KEY=OPENAI_API_KEY:latest,\
SENDGRID_API_KEY=SENDGRID_API_KEY:latest,\
FEDEX_API_KEY=FEDEX_API_KEY:latest,\
FEDEX_API_SECRET=FEDEX_API_SECRET:latest,\
FEDEX_ACCOUNT_NUMBER=FEDEX_ACCOUNT_NUMBER:latest,\
GITHUB_WEBHOOK_SECRET=GITHUB_WEBHOOK_SECRET:latest,\
DATABASE_URL=DATABASE_URL:latest,\
DATABASE_PASSWORD=DATABASE_PASSWORD:latest,\
DJANGO_SUPERUSER_PASSWORD=DJANGO_SUPERUSER_PASSWORD:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --quiet
    log "Deployed to Cloud Run"

    # Get and store the service URL
    local service_url
    service_url=$(gcloud run services describe "${SERVICE_NAME}" \
        --region="${REGION}" --project="${PROJECT_ID}" \
        --format='value(status.url)')

    # Update ALLOWED_HOSTS with service URL
    local service_host
    service_host=$(echo "${service_url}" | sed 's|https://||')

    gcloud run services update "${SERVICE_NAME}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --update-env-vars="ALLOWED_HOSTS=${service_host},CSRF_TRUSTED_ORIGINS=https://${service_host}" \
        --quiet
    log "Updated ALLOWED_HOSTS with: ${service_host}"
}

# --- Post-deploy ---
run_migrations() {
    info "Running database migrations..."

    local connection_name
    connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" --format='value(connectionName)')

    # Run migrations via Cloud Run Job
    gcloud run jobs create "${SERVICE_NAME}-migrate" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,migrate,--noinput" \
        --max-retries=1 \
        --quiet 2>/dev/null || \
    gcloud run jobs update "${SERVICE_NAME}-migrate" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,migrate,--noinput" \
        --max-retries=1 \
        --quiet

    gcloud run jobs execute "${SERVICE_NAME}-migrate" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --wait \
        --quiet
    log "Migrations complete"
}

create_superuser() {
    info "Creating Django admin superuser..."

    local connection_name
    connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" --format='value(connectionName)')

    gcloud run jobs create "${SERVICE_NAME}-createsuperuser" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True,DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=admin@indoorplant.com" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest,\
DJANGO_SUPERUSER_PASSWORD=DJANGO_SUPERUSER_PASSWORD:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,create_admin" \
        --max-retries=0 \
        --quiet 2>/dev/null || \
    gcloud run jobs update "${SERVICE_NAME}-createsuperuser" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True,DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=admin@indoorplant.com" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest,\
DJANGO_SUPERUSER_PASSWORD=DJANGO_SUPERUSER_PASSWORD:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,create_admin" \
        --max-retries=0 \
        --quiet

    gcloud run jobs execute "${SERVICE_NAME}-createsuperuser" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --wait \
        --quiet 2>/dev/null || warn "Admin user may already exist (this is OK)"
    log "Admin superuser setup complete"
}

seed_data() {
    info "Seeding sample products..."

    local connection_name
    connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" \
        --project="${PROJECT_ID}" --format='value(connectionName)')

    gcloud run jobs create "${SERVICE_NAME}-seeddata" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,seed_data" \
        --max-retries=0 \
        --quiet 2>/dev/null || \
    gcloud run jobs update "${SERVICE_NAME}-seeddata" \
        --image="${IMAGE_URI}" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="USE_HTTPS=True" \
        --set-secrets="\
SECRET_KEY=SECRET_KEY:latest,\
STRIPE_PUBLIC_KEY=STRIPE_PUBLIC_KEY:latest,\
STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,\
DATABASE_URL=DATABASE_URL:latest" \
        --add-cloudsql-instances="${connection_name}" \
        --command="python" \
        --args="manage.py,seed_data" \
        --max-retries=0 \
        --quiet

    gcloud run jobs execute "${SERVICE_NAME}-seeddata" \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --wait \
        --quiet 2>/dev/null || warn "Seed data may already exist (this is OK)"
    log "Sample products seeded"
}

# --- Print Summary ---
print_summary() {
    local service_url
    service_url=$(gcloud run services describe "${SERVICE_NAME}" \
        --region="${REGION}" --project="${PROJECT_ID}" \
        --format='value(status.url)' 2>/dev/null || echo "N/A")

    echo ""
    echo "=============================================="
    echo -e "${GREEN}  Deployment Complete!${NC}"
    echo "=============================================="
    echo ""
    echo -e "  App URL:     ${BLUE}${service_url}${NC}"
    echo -e "  Admin URL:   ${BLUE}${service_url}/admin/${NC}"
    echo ""
    echo "  Admin credentials:"
    echo "    Username: admin"
    echo "    Password: (stored in Secret Manager as DJANGO_SUPERUSER_PASSWORD)"
    echo ""
    echo "  Retrieve password:"
    echo "    gcloud secrets versions access latest --secret=DJANGO_SUPERUSER_PASSWORD"
    echo ""
    echo "  View logs:"
    echo "    gcloud run services logs read ${SERVICE_NAME} --region=${REGION}"
    echo ""
    echo "=============================================="
}

# --- Main ---
main() {
    local mode="${1:-full}"

    echo ""
    echo "=============================================="
    echo "  Indoor Plant Platform - GCP Deployment"
    echo "=============================================="
    echo ""

    check_prerequisites

    case "$mode" in
        --secrets-only)
            if [ -f ".env" ]; then
                sync_secrets
                info "Secrets synced. Redeploy to pick up changes:"
                echo "  ./deploy.sh --update"
            else
                warn "No .env found; secrets-only mode skipped (Secret Manager expected to be pre-populated)."
            fi
            ;;
        --update)
            build_and_deploy
            run_migrations
            create_superuser
            seed_data
            print_summary
            ;;
        *)
            enable_apis
            create_artifact_registry
            if [ -f ".env" ]; then
                sync_secrets
            else
                warn "Skipping secret sync (.env not found)."
            fi
            create_database
            create_storage_bucket
            setup_iam
            build_and_deploy
            run_migrations
            create_superuser
            seed_data
            print_summary
            ;;
    esac
}

main "$@"
