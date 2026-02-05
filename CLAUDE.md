# Indoor Plant E-Commerce Platform - AI Agent Guide

## Project Overview
Django-based multi-vendor e-commerce platform for indoor plants. Supports Buyer, Seller, and Admin roles with AI chatbot, Stripe payments, FedEx shipping, and inventory management.

## Tech Stack
- **Backend**: Django 5.1.2, Python 3.10+
- **Database**: MySQL (local/PythonAnywhere), PostgreSQL (Render)
- **Payments**: Stripe (PaymentIntent API)
- **AI**: OpenAI GPT-3.5-turbo
- **Shipping**: FedEx API (sandbox)
- **Email**: SendGrid
- **Static Files**: WhiteNoise
- **Frontend**: Bootstrap 5.3.3, CKEditor, Quill.js
- **Deployment**: Render.com (primary), PythonAnywhere (legacy)

## Project Structure
```
indoor_plant/          # Django project config (settings, urls, wsgi)
accounts/              # Custom user model (Buyer/Seller/Admin roles)
products/              # Product catalog, categories, tags, reviews
cart/                  # Shopping cart (auto-created per user via signals)
orders/                # Orders, shipping addresses, FedEx integration
payments/              # Stripe checkout flow
inventory/             # Barcode generation, stock tracking
ai/                    # OpenAI chatbot with product linking
analytics/             # Site visits & page view tracking (middleware)
admin_dashboard/       # Admin-only management views
templates/             # Global templates (base, home, partials)
static/                # CSS, JS, images
media/                 # User uploads (products, barcodes, banners)
```

## Key Architecture Decisions

### Custom User Model
- `accounts.CustomUser` extends `AbstractUser`
- Roles: BUYER, SELLER, ADMIN
- Custom manager: `CustomUserManager` with role-based querysets
- Slug auto-generated from business_name or username

### Authentication & Authorization
- `@login_required` for authenticated views
- `@user_passes_test(is_admin_user)` for admin views
- `@user_passes_test(is_seller_user)` for seller views
- Product edit/delete checks `product.seller == request.user`

### Cart System
- Cart auto-created via `post_save` signal on User creation
- OneToOne relationship: User -> Cart
- CartItem unique_together: (cart, product)

### Order Flow
Cart -> Select Shipping Address -> Review -> Stripe Payment -> Order Created

### Database
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- Uses `dj_database_url` for Render PostgreSQL
- SQLite for tests (see conftest.py)

## Conventions

### Code Style
- Django function-based views (majority), some class-based views
- Forms use `widget_tweaks` for Bootstrap styling
- URL namespacing per app (e.g., `products:product_detail`)
- Templates organized by app in `templates/<app_name>/`

### URL Patterns
- Products: `/products/`, `/products/<slug>/`
- Cart: `/cart/`, `/cart/add/<product_id>/`
- Orders: `/orders/`, `/orders/my/`, `/orders/seller/`
- Payments: `/payments/checkout/`, `/payments/process/`
- AI: `/ai/ask/`, `/ai/chat/`
- Admin: `/admin-dashboard/`

### Models
- All models use `BigAutoField` as default PK
- Timestamps: `created_at` (auto_now_add), `updated_at` (auto_now)
- Slugs auto-generated in `save()` method
- Product status auto-set based on stock in `save()`

### Forms
- Always use `commit=False` when setting seller on product forms
- Call `form.save_m2m()` after saving M2M fields (tags)

### Environment Variables (required)
- `SECRET_KEY`, `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`
- `OPENAI_API_KEY`, `SENDGRID_API_KEY`
- `FEDEX_API_KEY`, `FEDEX_API_SECRET`, `FEDEX_ACCOUNT_NUMBER`
- `GITHUB_WEBHOOK_SECRET`

## Testing

### Running Tests
```bash
python manage.py test                    # All tests
python manage.py test accounts           # Single app
python manage.py test --verbosity=2      # Verbose output
python manage.py test --parallel         # Parallel execution
```

### Test Database
Tests use SQLite in-memory by default (configured in conftest.py/test settings). No MySQL/PostgreSQL needed for tests.

### Writing Tests
- Place tests in each app's `tests.py` or `tests/` directory
- Use `TestCase` for DB tests, `SimpleTestCase` for no-DB tests
- Factory pattern: use helper methods to create test users, products, etc.
- Mock external APIs (Stripe, OpenAI, FedEx, SendGrid)
- Always test authorization (ensure buyers can't access seller views, etc.)

## Common Tasks

### Adding a new Django app
1. Create app: `python manage.py startapp <name>`
2. Add to `INSTALLED_APPS` in settings.py
3. Create URL patterns with namespace
4. Include in `indoor_plant/urls.py`

### Adding a new model
1. Define in app's `models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Register in `admin.py`

### Modifying the User model
- Edit `accounts/models.py` (CustomUser)
- If adding fields, make them nullable/blank for existing users
- Update forms in `accounts/forms.py`

## Gotchas
- `STRIPE_PUBLISHABLE_KEY`/`STRIPE_SECRET_KEY` must be set or settings.py raises `ImproperlyConfigured`
- Product `save()` auto-sets status to 'inactive' when stock=0
- Cart is auto-created on user creation (signal in `cart/models.py`)
- Analytics middleware runs on every request (may slow tests if not disabled)
- `CSRF_COOKIE_HTTPONLY = True` means AJAX needs `X-CSRFToken` header
