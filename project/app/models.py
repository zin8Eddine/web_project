from dateutil.relativedelta import relativedelta
from django.db import models
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

    total_tarif_reference = models.DecimalField(
        max_digits=9999, decimal_places=6, verbose_name='Total Tarif de Référence'
    )
    total_prix_public = models.DecimalField(
        max_digits=9999, decimal_places=6, verbose_name='Total Prix Public'
    )

    @classmethod
    def update_totals(cls):
        consommations = cls.objects.all()
        for consommation in consommations:
            consommation.total_tarif_reference = consommation.medicament.tarifReference * consommation.quantite
            consommation.total_prix_public = consommation.medicament.prixPublic * consommation.quantite
            consommation.save()

    def save(self, *args, **kwargs):
        self.total_tarif_reference = self.medicament.tarifReference * self.quantite
        self.total_prix_public = self.medicament.prixPublic * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Consommation {self.id} - {self.medicament.nomMedicament}"
