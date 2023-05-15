from django.contrib import admin
from .models import JobCard, Customer, Images


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number', 'alt_contact_number', 'address')
    search_fields = ('name', 'email', 'contact_number', 'alt_contact_number', 'address')


@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product_name', 'job_status', 'last_modified_at')
    list_filter = ('job_status',)
    search_fields = ('customer__name', 'product_name', 'job_number')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(JobCardAdmin, self).get_fieldsets(request, obj)

        # if obj:
        #     customer_fields = ('customer__name', 'customer__email', 'customer__contact_number', 'customer__alt_contact_number', 'customer__address')
        #     fieldsets[0][1]['fields'] = customer_fields + fieldsets[0][1]['fields']
        #
        #     for field in customer_fields:
        #         self.readonly_fields += (field,)

        return fieldsets

    def customer__name(self, obj):
        return obj.customer.name

    def customer__email(self, obj):
        return obj.customer.email

    def customer__contact_number(self, obj):
        return obj.customer.contact_number

    def customer__alt_contact_number(self, obj):
        return obj.customer.alt_contact_number

    def customer__address(self, obj):
        return obj.customer.address

    customer__name.short_description = 'Name'
    customer__email.short_description = 'Email'
    customer__contact_number.short_description = 'Contact Number'
    customer__alt_contact_number.short_description = 'Alt. Contact Number'
    customer__address.short_description = 'Address'


admin.site.register(Images)
