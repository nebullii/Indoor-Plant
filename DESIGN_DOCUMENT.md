# Indoor Plant E-Commerce Platform - System Design Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Overview](#architecture-overview)
4. [Data Models and Schema](#data-models-and-schema)
5. [API Design](#api-design)
6. [Security Considerations](#security-considerations)
7. [Scalability and Performance](#scalability-and-performance)
8. [Monitoring and Analytics](#monitoring-and-analytics)
9. [Deployment Strategy](#deployment-strategy)
10. [Future Enhancements](#future-enhancements)

## Executive Summary

The Indoor Plant E-Commerce Platform is a comprehensive Django-based web application designed to facilitate the buying and selling of indoor plants. The system supports multiple user roles (buyers, sellers, administrators) with features including product catalog management, shopping cart functionality, secure payments via Stripe, inventory tracking, AI-powered chatbot support, and comprehensive analytics.

**Key Metrics:**
- Multi-tenant architecture supporting unlimited sellers
- Real-time inventory management
- Integrated payment processing
- AI-powered customer support
- Comprehensive analytics and reporting

## System Overview

### Core Features
- **User Management**: Role-based authentication (Buyer, Seller, Admin)
- **Product Catalog**: Rich product listings with categories, tags, and reviews
- **Shopping Cart**: Session-based cart management with persistence
- **Order Processing**: End-to-end order management with tracking
- **Payment Integration**: Secure Stripe payment processing
- **Inventory Management**: Automated inventory tracking with barcode generation
- **AI Chatbot**: OpenAI-powered plant care assistance
- **Analytics**: Site visits, page views, and business metrics
- **Admin Dashboard**: Comprehensive administrative interface

### Technology Stack
```
Frontend:
- HTML5/CSS3/JavaScript
- Bootstrap 5.3.3
- CKEditor (Rich Text Editing)
- Quill.js (Product Descriptions)

Backend:
- Django 5.1.2 (Python Web Framework)
- Python 3.6+
- MySQL Database
- WhiteNoise (Static File Serving)

Third-party Services:
- Stripe (Payment Processing)
- OpenAI GPT (AI Chatbot)
- FedEx API (Shipping)
- SendGrid (Email Services)

Infrastructure:
- PythonAnywhere (Hosting)
- AWS S3 (Media Storage - Optional)
- MySQL Database
```

## Architecture Overview

### System Architecture Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django App    │    │   Database      │
│   (Templates)   │◄──►│   (Backend)     │◄──►│   (MySQL)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼───┐ ┌─────▼─────┐ ┌───▼────┐
            │  Stripe   │ │  OpenAI   │ │ FedEx  │
            │ Payments  │ │ Chatbot   │ │Shipping│
            └───────────┘ └───────────┘ └────────┘
```

### Application Architecture
The system follows Django's MVT (Model-View-Template) pattern with the following application structure:

```
indoor_plant/               # Main project settings
├── accounts/              # User authentication and profiles
├── products/              # Product catalog management
├── cart/                 # Shopping cart functionality
├── orders/               # Order processing and tracking
├── payments/             # Stripe payment integration
├── inventory/            # Inventory management and barcodes
├── ai/                   # OpenAI chatbot integration
├── analytics/            # Site analytics and tracking
└── admin_dashboard/      # Administrative interface
```

## Data Models and Schema

### Core Entities

#### User Management
```python
CustomUser
├── role: BUYER | SELLER | ADMIN
├── business_name: CharField (for sellers)
├── store_banner: ImageField
├── address: TextField
├── slug: SlugField (unique storefront URL)
└── is_verified: BooleanField
```

#### Product Catalog
```python
Category
├── name: CharField
├── type: indoor | outdoor
├── slug: SlugField
└── is_active: BooleanField

Product
├── name: CharField
├── description: TextField
├── price: DecimalField
├── image: ImageField
├── seller: ForeignKey(CustomUser)
├── category: ForeignKey(Category)
├── tags: ManyToManyField(Tag)
├── stock: PositiveIntegerField
├── status: draft | active | inactive
├── sku: CharField (unique)
├── slug: SlugField (unique)
├── meta_title/meta_description: SEO fields
├── about: TextField (plant information)
└── care_tip: TextField (care instructions)

Review
├── product: ForeignKey(Product)
├── user: ForeignKey(CustomUser)
├── rating: 1-5 stars
├── comment: TextField
└── unique_together: (product, user)
```

#### Order Management
```python
ShippingAddress
├── user: ForeignKey(CustomUser)
├── full_name: CharField
├── address: CharField
├── city/state/postal_code: CharField
├── country: CountryField
├── phone_number: CharField
└── is_default: BooleanField

Order
├── user: ForeignKey(CustomUser)
├── shipping_address: ForeignKey(ShippingAddress)
├── status: PENDING | PROCESSING | SHIPPED | DELIVERED | CANCELLED
├── shipping_cost: DecimalField
├── tracking_number: CharField
└── Properties: subtotal, total

OrderItem
├── order: ForeignKey(Order)
├── product: ForeignKey(Product)
├── quantity: PositiveIntegerField
└── price: DecimalField (snapshot at purchase time)
```

#### Cart System
```python
Cart
├── user: OneToOneField(CustomUser)
├── Methods: get_total_items(), get_subtotal(), get_total()
└── Auto-created via Django signals

CartItem
├── cart: ForeignKey(Cart)
├── product: ForeignKey(Product)
├── quantity: PositiveIntegerField
└── unique_together: (cart, product)
```

### Database Schema Relationships
```
CustomUser (1) ──── (∞) Product
CustomUser (1) ──── (1) Cart
Cart (1) ──── (∞) CartItem
CustomUser (1) ──── (∞) Order
Order (1) ──── (∞) OrderItem
Product (∞) ──── (1) Category
Product (∞) ──── (∞) Tag
Product (1) ──── (∞) Review
```

## API Design

### RESTful Endpoints

#### Authentication
```
POST   /accounts/signup/          # User registration
POST   /accounts/login/           # User login
POST   /accounts/logout/          # User logout
GET    /accounts/profile/         # User profile view
POST   /accounts/profile/update/  # Profile updates
```

#### Product Management
```
GET    /products/                 # Product listing with filters
GET    /products/<slug>/          # Product detail view
POST   /products/add/             # Add new product (sellers only)
PUT    /products/<id>/edit/       # Edit product (seller/admin)
DELETE /products/<id>/delete/     # Delete product (seller/admin)
GET    /products/search/          # Product search
```

#### Cart Operations
```
GET    /cart/                     # View cart
POST   /cart/add/<product_id>/    # Add to cart
PUT    /cart/update/<item_id>/    # Update quantity
DELETE /cart/remove/<item_id>/    # Remove from cart
POST   /cart/clear/               # Clear cart
```

#### Order Processing
```
GET    /orders/                   # Order history
GET    /orders/<id>/              # Order details
POST   /orders/create/            # Create order
PUT    /orders/<id>/status/       # Update order status (seller/admin)
GET    /orders/tracking/<number>/ # Track shipment
```

#### Payment Integration
```
POST   /payments/create-intent/   # Create Stripe payment intent
POST   /payments/webhook/         # Stripe webhook handler
GET    /payments/success/         # Payment success page
GET    /payments/cancel/          # Payment cancelled page
```

### Data Flow Patterns

#### Purchase Flow
```
1. User browses products → Product catalog
2. Add to cart → Cart system updates
3. Proceed to checkout → Create order (PENDING)
4. Payment processing → Stripe integration
5. Payment success → Order status (PROCESSING)
6. Inventory deduction → Stock updates
7. Shipping label generation → FedEx API
8. Order fulfillment → Status (SHIPPED)
```

## Security Considerations

### Authentication & Authorization
- **Django's built-in authentication system** with custom user model
- **Role-based access control** (RBAC) for buyers, sellers, and administrators
- **Session management** with secure cookies
- **CSRF protection** on all forms
- **Password validation** with Django's validators

### Data Protection
```python
# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Environment-based configuration
SECRET_KEY = os.getenv("SECRET_KEY")
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### Payment Security
- **PCI DSS compliance** through Stripe integration
- **No sensitive payment data storage** on servers
- **Webhook signature verification** for payment callbacks
- **SSL/TLS encryption** for all payment transactions

### Input Validation & Sanitization
- **Django's ORM** prevents SQL injection
- **Form validation** on all user inputs
- **Rich text editor sanitization** (CKEditor/Quill)
- **File upload restrictions** for images

### API Security
- **Rate limiting** (recommended for production)
- **Input sanitization** on all endpoints
- **Proper error handling** without information leakage
- **Logging and monitoring** for suspicious activities

## Scalability and Performance

### Current Architecture Limitations
- **Single MySQL database** - potential bottleneck
- **Server-side rendering** - limited client-side caching
- **Media files on local storage** - bandwidth constraints
- **No caching layer** - repeated database queries

### Recommended Scaling Strategies

#### Database Optimization
```python
# Implement database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 3600,  # Connection pooling
    }
}

# Query optimization with select_related and prefetch_related
products = Product.objects.select_related('category', 'seller')\
                         .prefetch_related('tags', 'reviews')
```

#### Caching Strategy
```python
# Redis caching implementation
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache frequently accessed data
@cache_page(60 * 15)  # 15 minutes
def product_list(request):
    # Cached product listings
    pass
```

#### Media and Static Files
```python
# AWS S3 integration for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-west-2'
```

#### Load Balancing & Horizontal Scaling
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Load Balancer│────│Django App 1 │    │Django App 2 │
└─────────────┘    └─────────────┘    └─────────────┘
                            │                 │
                    ┌───────────────────────────┐
                    │     Shared Database       │
                    │     (MySQL/PostgreSQL)    │
                    └───────────────────────────┘
```

### Performance Metrics & Monitoring
- **Response time targets**: < 200ms for product pages
- **Availability**: 99.9% uptime
- **Database query optimization**: < 50ms average query time
- **Image optimization**: WebP format, lazy loading
- **CDN implementation**: CloudFlare or AWS CloudFront

## Monitoring and Analytics

### Built-in Analytics System
```python
# Site visit tracking
class SiteVisit(models.Model):
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    first_seen = models.DateTimeField(auto_now_add=True)

# Page view analytics
class PageView(models.Model):
    session_key = models.CharField(max_length=40)
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Business Intelligence
- **Sales analytics**: Revenue tracking, product performance
- **User behavior**: Cart abandonment, conversion rates
- **Inventory insights**: Stock levels, reorder points
- **Seller performance**: Sales volume, customer ratings

### External Monitoring Tools
```python
# Recommended integrations
- Google Analytics 4
- Sentry (Error tracking)
- New Relic (APM)
- DataDog (Infrastructure monitoring)
```

### Key Performance Indicators (KPIs)
- **Conversion Rate**: Visitors to purchasers
- **Average Order Value (AOV)**
- **Customer Lifetime Value (CLV)**
- **Cart Abandonment Rate**
- **Seller Onboarding Rate**
- **Product Catalog Growth**

## Deployment Strategy

### Current Deployment (PythonAnywhere)
```yaml
Environment: Production
Platform: PythonAnywhere
Database: MySQL
Static Files: WhiteNoise
Domain: nevus.pythonanywhere.com
```

### Recommended Production Deployment

#### Containerization with Docker
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "indoor_plant.wsgi:application"]
```

#### Infrastructure as Code
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/indoor_plant
      
  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=indoor_plant
      - MYSQL_ROOT_PASSWORD=rootpass
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

#### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Run tests
          python manage.py test
          # Deploy to server
          # Update database migrations
          # Collect static files
```

## Future Enhancements

### Short-term Roadmap (3-6 months)
1. **Mobile Application**: React Native or Flutter app
2. **Advanced Search**: Elasticsearch integration
3. **Recommendation Engine**: ML-based product suggestions
4. **Multi-language Support**: Django i18n implementation
5. **Advanced Analytics Dashboard**: Real-time business metrics

### Medium-term Roadmap (6-12 months)
1. **Microservices Architecture**: Break down monolith
2. **Event-driven Architecture**: Redis/RabbitMQ messaging
3. **Advanced AI Features**: Plant disease detection via image recognition
4. **Subscription Services**: Plant care subscription boxes
5. **Social Features**: User reviews, plant care communities

### Long-term Vision (12+ months)
1. **IoT Integration**: Smart plant sensors and monitoring
2. **AR/VR Features**: Virtual plant placement
3. **Blockchain Integration**: Supply chain transparency
4. **International Expansion**: Multi-currency, international shipping
5. **Marketplace Evolution**: Third-party seller ecosystem

### Technical Debt & Improvements
1. **Test Coverage**: Achieve 90%+ test coverage
2. **Documentation**: Comprehensive API documentation
3. **Code Quality**: Implement SonarQube analysis
4. **Security Audits**: Regular penetration testing
5. **Performance Optimization**: Database query optimization

---

## Conclusion

The Indoor Plant E-Commerce Platform represents a well-architected Django application with solid foundations for growth. The current implementation provides essential e-commerce functionality with room for significant enhancement in scalability, performance, and feature richness.

**Key Strengths:**
- Modular Django architecture
- Comprehensive user role management
- Integrated payment processing
- AI-powered customer support
- Built-in analytics tracking

**Areas for Improvement:**
- Database scalability
- Caching implementation
- Mobile-first design
- Advanced search capabilities
- Microservices migration

This design document serves as a roadmap for the platform's continued development and evolution into a scalable, feature-rich e-commerce solution.

---

*Document Version: 1.0*  
*Last Updated: August 10, 2025*  
*Author: System Analysis Team*