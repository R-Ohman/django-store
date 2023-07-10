from django.apps import AppConfig


class ProductsConfig(AppConfig):
    ProductsConfig = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        import products.signals
