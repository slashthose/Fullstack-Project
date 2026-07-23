from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from import_export.admin import ImportExportModelAdmin
from core.models import *


# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
class ProductResource(resources.ModelResource):
    category = fields.Field(
    column_name='category',
    attribute='category',
    widget=ManyToManyWidget(Category, field='category_name', separator=',')
)

    class Meta:
        model = Product
        import_id_fields = ('name',)
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'name', 'category', 'price', 'img', 'desc')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'price', 'desc')
    filter_horizontal = ('category',)

admin.site.register(Wishlist)
