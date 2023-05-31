from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta
from app.models import AssurerMalade80, AssurerMalade100, AssurerMaladePathologieAssociation

class AssurerMaladeAdmin(admin.ModelAdmin):
    readonly_fields = ('dateFinDroit',)

    def save_model(self, request, obj, form, change):
        if not change:  # Only calculate dateFinDroit when creating a new instance
            # Subtract one day from 12 months
            delta = relativedelta(months=12, days=-1)
            obj.dateFinDroit = obj.dateDebutDroit + delta
        else:
            # Calculate dateFinDroit if dateDebutDroit is modified
            previous_obj = self.model.objects.get(pk=obj.pk)
            if previous_obj.dateDebutDroit != obj.dateDebutDroit:
                delta = relativedelta(months=12, days=-1)
                obj.dateFinDroit = obj.dateDebutDroit + delta

        super().save_model(request, obj, form, change)

class AssurerMalade80Admin(AssurerMaladeAdmin):
    search_fields = ['matricule']


class AssurerMalade100Admin(AssurerMaladeAdmin):
    search_fields = ['matricule']

admin.site.register(AssurerMalade100, AssurerMalade100Admin)
admin.site.register(AssurerMalade80, AssurerMalade80Admin)





# admin.site.register(AssurerMaladePathologieAssociation, AssurerMaladePathologieAssociationAdmin)

# class AssurerMaladePathologieAssociationAdmin(admin.ModelAdmin):
#     ordering = ['assurer_malade__nom', 'pathologie__nomPathologie']
#     list_filter = ['pathologie', 'assurer_malade__assurermalade80' ,'assurer_malade__assurermalade100']
#     search_fields = ['assurer_malade__matricule', 'pathologie__id']
#     list_display = ['assurer_malade', 'pathologie']


# admin.site.register(AssurerMaladePathologieAssociation, AssurerMaladePathologieAssociationAdmin)


class AssurerMaladeFilter(admin.SimpleListFilter):
    title = _('Assurer Malade')
    parameter_name = 'assurer_malade'

    def lookups(self, request, model_admin):
        return (
            ('assurermalade100', _('Assurer Malade 100%')),
            ('assurermalade80', _('Assurer Malade 80%')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'assurermalade100':
            return queryset.filter(assurer_malade__assurermalade100__isnull=False)
        if self.value() == 'assurermalade80':
            return queryset.filter(assurer_malade__assurermalade80__isnull=False)

        return queryset


class AssurerMaladePathologieAssociationAdmin(admin.ModelAdmin):
    ordering = ['assurer_malade__nom', 'pathologie__nomPathologie']
    list_filter = [AssurerMaladeFilter, 'pathologie']
    search_fields = ['assurer_malade__matricule', 'pathologie__id']
    list_display = ['assurer_malade', 'pathologie']


admin.site.register(AssurerMaladePathologieAssociation, AssurerMaladePathologieAssociationAdmin)