from django.shortcuts import render

# Create your views here.


def index(request):
    context = {
        'title': 'Store',
        'is_promotion': False,
    }
    return render(request, 'products/index.html', context)

def products(request):
    context = {
        'products' : [
            {
                'name': 'Худи черного цвета с монограммами adidas Originals',
                'price': 6_090,
                'img': '/static/vendor/img/products/Adidas-hoodie.png',
                'description': 'Мягкая ткань для свитшотов. Стиль и комфорт – это образ жизни.',
            },
            {
                'name': 'Синяя куртка The North Face',
                'price': 23_730,
                'img': '/static/vendor/img/products/Blue-jacket-The-North-Face.png',
                'description': 'Гладкая ткань. Водонепроницаемое покрытие. Легкий и теплый пуховый наполнитель.',
            },
            {
                'name': 'Коричневый спортивный oversized-топ ASOS DESIGN',
                'price': 3_390,
                'img': '/static/vendor/img/products/Brown-sports-oversized-top-ASOS-DESIGN.png',
                'description': 'Мягкий трикотаж. Эластичный материал.',
            },
            {
                'name': 'Черный рюкзак Nike Heritage',
                'price': 2_340,
                'img': '/static/vendor/img/products/Black-Nike-Heritage-backpack.png',
                'description': 'Плотная ткань. Легкий и прочный материал.',
            },
        ]
    }

    return render(request, 'products/products.html', context)