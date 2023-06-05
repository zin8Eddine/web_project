from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone


class AssurerMalade(models.Model):
    matricule = models.IntegerField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    lieuAdress = models.CharField(max_length=255)
    telephone = models.IntegerField()
    assuerMdp = models.CharField(max_length=255)
    statusAjour = models.BooleanField()
    dateDebutDroit = models.DateField()
    dateFinDroit = models.DateField()

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def getFullName(self):
        return f"{self.prenom} {self.nom}"

    def save(self, *args, **kwargs):
        if not self.pk:
            # Only calculate dateFinDroit when creating a new instance
            self.dateFinDroit = self.dateDebutDroit + relativedelta(months=12)

        if timezone.now().date() >= self.dateFinDroit:
            self.statusAjour = False
        else:
            self.statusAjour = True


        super().save(*args, **kwargs)

            

    def login(self, email, password):
        if self.emailAdress == email and self.assuerMdp == password:
            return True
        return False



# subcalsses AssurerMalade100 and AssurerMalade80
    
class AssurerMalade100(AssurerMalade):
    tauxPriseCharge = 100

    class Meta:
        verbose_name_plural = "Assurer malade 100%"
        

class AssurerMalade80(AssurerMalade):
    tauxPriseCharge = 80

    class Meta:
        verbose_name_plural = "Assurer malade 80%"





# ---------------------------calss patholigie-----------


class Pathologie(models.Model):
    TYPE_DE_MALADIE_CHOICES = [(f'c{i}', f'c{i}') for i in range(1, 28)]
    nomPathologie = models.CharField(
        max_length=255, choices=TYPE_DE_MALADIE_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.nomPathologie


class AssurerMaladePathologieAssociation(models.Model):
    assurer_malade = models.ForeignKey(
        AssurerMalade, on_delete=models.CASCADE, related_name='pathologie_associations'
    )
    pathologie = models.ForeignKey(Pathologie, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Assurer Malade - Pathologie Associations"

    def __str__(self):
        return f"{self.assurer_malade} - {self.pathologie}"
    
class Medicament(models.Model):
        FORME_CHOICES = [
            ('comprimé', 'Comprimé'),
            ('capsule', 'Capsule'),
            ('sirop', 'Sirop'),
            ('suspension', 'Suspension'),
            ('gelule', 'Gélule'),
            ('patch', 'Patch'),
            ('suppositoire', 'Suppositoire'),
            ('inhalateur', 'Inhalateur'),
        ]

        CodeMedicament = models.CharField(
            max_length=11, primary_key=True, verbose_name='Code Médicament')
        nomMedicament = models.CharField(
            max_length=255, verbose_name='Nom Médicament')
        forme = models.CharField(
            max_length=255, choices=FORME_CHOICES, verbose_name='Forme')
        dosage = models.CharField(max_length=255, verbose_name='Dosage')
        Conditionnement = models.CharField(
            max_length=255, verbose_name='Conditionnement')
        prixPublic = models.DecimalField(
            max_digits=9999, decimal_places=6, verbose_name='Prix Public')
        tarifReference = models.DecimalField(
            max_digits=9999, decimal_places=6, verbose_name='Tarif de Référence')

        def __str__(self):
            return self.nomMedicament


    
    
class Consommation(models.Model):
    assurer_malade = models.ForeignKey(
        AssurerMalade, on_delete=models.CASCADE, related_name='consommations'
    )
    medicament = models.ForeignKey(
        Medicament, on_delete=models.CASCADE, verbose_name='Médicament'
    )
    quantite = models.PositiveIntegerField(verbose_name='Quantité')

    tarif_reference_Qnt = models.DecimalField(
        max_digits=9999, decimal_places=6, verbose_name='Tarif de Référence par quantite'
    )
    prix_public_Qnt = models.DecimalField(
        max_digits=9999, decimal_places=6, verbose_name='Total Prix Public par quantite'
    )

    @classmethod
    def update_totals(cls):
        consommations = cls.objects.all()
        for consommation in consommations:
            consommation.tarif_reference_Qnt = consommation.medicament.tarifReference * consommation.quantite
            consommation.prix_public_Qnt = consommation.medicament.prixPublic * consommation.quantite
            consommation.save()

    def save(self, *args, **kwargs):
        self.tarif_reference_Qnt = self.medicament.tarifReference * self.quantite
        self.prix_public_Qnt = self.medicament.prixPublic * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consommation {self.id} - {self.medicament.nomMedicament}"

class ConsommationTotal(models.Model):
    dataDebutTretment = models.DateField()
    dateFinTretment = models.DateField()
    total_tarif_reference = models.DecimalField(max_digits=9999, decimal_places=6)
    total_prix_public = models.DecimalField(max_digits=9999, decimal_places=6)
    consommations = models.ManyToManyField(Consommation, related_name='consommation_totals')

    @classmethod
    def update_totals(cls):
        # Calculate dataDebutTretment and dateFinTretment
        data_debut = Consommation.objects.earliest('date').date
        date_fin = data_debut + timedelta(days=90)

        # Calculate total_tarif_reference and total_prix_public
        totals = Consommation.objects.aggregate(
            total_tarif_reference=Sum('tarif_reference_Qnt'),
            total_prix_public=Sum('prix_public_Qnt')
        )

        # Get or create the ConsommationTotal instance
        consommation_total, created = cls.objects.get_or_create(
            defaults={
                'dataDebutTretment': data_debut,
                'dateFinTretment': date_fin,
                'total_tarif_reference': totals['total_tarif_reference'],
                'total_prix_public': totals['total_prix_public'],
            }
        )

        # Update the consommations association
        consommation_total.consommations.set(Consommation.objects.all())

    def __str__(self):
        return f"ConsommationTotal - {self.id}"
