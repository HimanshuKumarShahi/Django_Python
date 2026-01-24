from django.contrib import admin
from .models import ChaiVarity,ChaiReview,ChaiCertificate,Store

# Register your models here.
class ChaiReviewInline(admin.TabularInline):
    model=ChaiReview
    extra=1

class ChaiVarietyAdmin(admin.ModelAdmin):
    list_display=('name','types','date_added')
    inlines=[ChaiReviewInline]

class StoreAdmin(admin.ModelAdmin):
    list_display=('name','location')
    filter_horizontal=('chai_Varities',)

class ChaiCertificateAdmin(admin.ModelAdmin):
    list_display=('chai','certificate_number')

admin.site.register(ChaiVarity,ChaiVarietyAdmin)
admin.site.register(Store,StoreAdmin)
admin.site.register(ChaiCertificate,ChaiCertificateAdmin)