from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta
from app.models import AssurerMalade80, AssurerMalade100, AssurerMaladePathologieAssociation,Pathologie

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



class PathologieAdmin(admin.ModelAdmin):
    list_display = ['nomPathologie']


admin.site.register(Pathologie, PathologieAdmin)



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
    search_fields = ['assurer_malade__matricule', 'pathologie__id','pathologie__nomPathologie']
    list_display = ['assurer_malade', 'pathologie','assurer_malade_taux']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pathologie":
            kwargs["queryset"] = Pathologie.objects.all()
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
    
    def assurer_malade_taux(self, obj):
        if hasattr(obj.assurer_malade, 'assurermalade100'):
            return '100'
        elif hasattr(obj.assurer_malade, 'assurermalade80'):
            return '80'
        return ''

    assurer_malade_taux.short_description = 'Taux Prise en Charge'


admin.site.register(AssurerMaladePathologieAssociation, AssurerMaladePathologieAssociationAdmin)