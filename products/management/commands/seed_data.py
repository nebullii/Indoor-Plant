import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from products.models import Category, Tag, Product

User = get_user_model()

CATEGORIES = [
    {'name': 'Tropical Plants', 'slug': 'tropical-plants', 'type': 'indoor',
     'description': 'Lush tropical plants that thrive indoors'},
    {'name': 'Succulents', 'slug': 'succulents', 'type': 'indoor',
     'description': 'Low-maintenance succulents perfect for any space'},
    {'name': 'Ferns', 'slug': 'ferns', 'type': 'indoor',
     'description': 'Beautiful ferns that love humidity'},
    {'name': 'Herbs', 'slug': 'herbs', 'type': 'indoor',
     'description': 'Fresh herbs you can grow on your windowsill'},
    {'name': 'Flowering Plants', 'slug': 'flowering-plants', 'type': 'indoor',
     'description': 'Colorful flowering plants to brighten your home'},
]

TAGS = [
    {'name': 'Low Light', 'slug': 'low-light'},
    {'name': 'Pet Friendly', 'slug': 'pet-friendly'},
    {'name': 'Air Purifying', 'slug': 'air-purifying'},
    {'name': 'Beginner Friendly', 'slug': 'beginner-friendly'},
    {'name': 'Low Maintenance', 'slug': 'low-maintenance'},
]

PRODUCTS = [
    {
        'name': 'Snake Plant',
        'category': 'tropical-plants',
        'price': 24.99,
        'cost_price': 12.00,
        'stock': 50,
        'tags': ['low-light', 'air-purifying', 'beginner-friendly', 'low-maintenance'],
        'description': 'The Snake Plant (Sansevieria) is one of the most popular and hardy indoor plants. It thrives in low light and requires minimal watering.',
        'about': 'Native to West Africa, this striking plant features tall, sword-like leaves with green banding.',
        'care_tip': 'Water every 2-3 weeks. Allow soil to dry completely between waterings. Tolerates low to bright indirect light.',
        'featured': True,
        'color': (34, 120, 60),
    },
    {
        'name': 'Pothos Golden',
        'category': 'tropical-plants',
        'price': 18.99,
        'cost_price': 8.00,
        'stock': 75,
        'tags': ['low-light', 'air-purifying', 'beginner-friendly'],
        'description': 'Golden Pothos is a trailing vine with heart-shaped leaves splashed with golden yellow variegation.',
        'about': 'One of the easiest houseplants to grow, perfect for hanging baskets or shelves.',
        'care_tip': 'Water when top inch of soil is dry. Bright indirect light for best variegation, but tolerates low light.',
        'featured': True,
        'hot_selling': True,
        'color': (80, 140, 50),
    },
    {
        'name': 'Aloe Vera',
        'category': 'succulents',
        'price': 15.99,
        'cost_price': 6.00,
        'stock': 60,
        'tags': ['beginner-friendly', 'low-maintenance'],
        'description': 'Aloe Vera is a versatile succulent known for its medicinal properties. The gel inside the leaves soothes burns and skin irritations.',
        'about': 'A staple in homes worldwide, Aloe Vera is both decorative and functional.',
        'care_tip': 'Water deeply but infrequently. Needs bright indirect sunlight. Use well-draining soil.',
        'hot_selling': True,
        'color': (100, 170, 80),
    },
    {
        'name': 'Boston Fern',
        'category': 'ferns',
        'price': 22.99,
        'cost_price': 10.00,
        'stock': 40,
        'tags': ['pet-friendly', 'air-purifying'],
        'description': 'The Boston Fern is a classic houseplant with graceful, arching fronds. It is an excellent air purifier and safe for pets.',
        'about': 'A Victorian-era favorite that adds lush greenery to any room.',
        'care_tip': 'Keep soil consistently moist. Loves humidity — mist regularly. Bright indirect light.',
        'color': (50, 130, 50),
    },
    {
        'name': 'Peace Lily',
        'category': 'flowering-plants',
        'price': 28.99,
        'cost_price': 14.00,
        'stock': 35,
        'tags': ['low-light', 'air-purifying'],
        'description': 'The Peace Lily produces elegant white spathes and glossy dark green leaves. It is one of the best plants for improving indoor air quality.',
        'about': 'NASA-approved air purifier that removes toxins like formaldehyde and benzene.',
        'care_tip': 'Water when leaves start to droop slightly. Low to medium indirect light. Keep away from cold drafts.',
        'featured': True,
        'color': (40, 100, 55),
    },
    {
        'name': 'Basil',
        'category': 'herbs',
        'price': 8.99,
        'cost_price': 3.00,
        'stock': 100,
        'tags': ['beginner-friendly'],
        'description': 'Fresh Sweet Basil is a must-have kitchen herb. Grow it on your windowsill for a constant supply of aromatic leaves.',
        'about': 'Essential for Italian and Thai cooking. Pinch off flowers to encourage bushy growth.',
        'care_tip': 'Water regularly to keep soil moist. Needs 6-8 hours of direct sunlight. Harvest from the top.',
        'color': (60, 140, 40),
    },
    {
        'name': 'ZZ Plant',
        'category': 'tropical-plants',
        'price': 32.99,
        'cost_price': 16.00,
        'stock': 30,
        'tags': ['low-light', 'low-maintenance', 'beginner-friendly'],
        'description': 'The ZZ Plant (Zamioculcas zamiifolia) features glossy, dark green leaves on graceful stems. Nearly indestructible.',
        'about': 'Thrives on neglect — perfect for offices and busy plant parents.',
        'care_tip': 'Water every 2-3 weeks. Tolerates low light to bright indirect light. Avoid overwatering.',
        'hot_selling': True,
        'color': (25, 90, 40),
    },
    {
        'name': 'Rosemary',
        'category': 'herbs',
        'price': 11.99,
        'cost_price': 4.50,
        'stock': 55,
        'tags': ['low-maintenance'],
        'description': 'Rosemary is a fragrant evergreen herb perfect for indoor growing. Great for cooking and aromatherapy.',
        'about': 'Mediterranean native that doubles as a culinary herb and natural air freshener.',
        'care_tip': 'Water when soil is dry. Needs bright direct light (south-facing window). Good drainage is essential.',
        'color': (70, 120, 70),
    },
]


def generate_placeholder_image(color, name):
    """Generate a simple colored placeholder image with plant name."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # Fallback: 1x1 pixel PNG
        import struct, zlib
        raw = struct.pack('>B3B', 0, *color)
        img_data = b'\x89PNG\r\n\x1a\n'
        # Minimal valid PNG
        return ContentFile(img_data, name=f'{slugify(name)}.png')

    img = Image.new('RGB', (600, 600), color)
    draw = ImageDraw.Draw(img)

    # Draw plant name centered
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except (OSError, IOError):
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (600 - text_w) // 2
    y = (600 - text_h) // 2
    # White text with slight shadow
    draw.text((x + 2, y + 2), name, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), name, fill=(255, 255, 255), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return ContentFile(buffer.getvalue(), name=f'{slugify(name)}.jpg')


class Command(BaseCommand):
    help = 'Seed the database with sample categories, tags, and products (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete existing seed data before creating')

    def handle(self, *args, **options):
        if options['clear']:
            Product.objects.filter(seller__username='plantshop').delete()
            self.stdout.write(self.style.WARNING('Cleared existing seed products.'))

        # Create categories
        categories = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
            categories[cat.slug] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')

        # Create tags
        tags = {}
        for tag_data in TAGS:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data,
            )
            tags[tag.slug] = tag
            if created:
                self.stdout.write(f'  Created tag: {tag.name}')

        # Create seller account for seed products
        seller, created = User.objects.get_or_create(
            username='plantshop',
            defaults={
                'email': 'plantshop@example.com',
                'role': 'SELLER',
                'is_verified': True,
                'business_name': 'Indoor Plant Shop',
            },
        )
        if created:
            seller.set_unusable_password()
            seller.save()
            self.stdout.write(f'  Created seller: {seller.username}')

        # Create products
        created_count = 0
        for product_data in PRODUCTS:
            if Product.objects.filter(slug=slugify(product_data['name'])).exists():
                self.stdout.write(f'  Skipped (exists): {product_data["name"]}')
                continue

            color = product_data.pop('color')
            tag_slugs = product_data.pop('tags')
            category_slug = product_data.pop('category')

            image = generate_placeholder_image(color, product_data['name'])

            product = Product(
                seller=seller,
                category=categories[category_slug],
                image=image,
                **product_data,
            )
            product.save()
            product.tags.set([tags[s] for s in tag_slugs])
            created_count += 1
            self.stdout.write(f'  Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {created_count} products created, '
            f'{len(PRODUCTS) - created_count} skipped.'
        ))
