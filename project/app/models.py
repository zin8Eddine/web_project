
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from twilio.rest import Client


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

        # Send the assuerMdp to the phone number
        account_sid = 'ACcf8f6629c8f1f587c0bd67ab5d644843'
        auth_token = '465c6c80ce8c165fd1294b0740c7cc10'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='+13157108505',
            body='mihmioh',
            to='+213559587950'
        )

        return super().save(*args, **kwargs)

    def login(self, email, password):
        if self.emailAdress == email and self.assuerMdp == password:
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            # Only calculate dateFinDroit when creating a new instance
            self.dateFinDroit = self.dateDebutDroit + relativedelta(months=12)

        if timezone.now().date() >= self.dateFinDroit:
            self.statusAjour = False
        else:
            self.statusAjour = True

        super().save(*args, **kwargs)
        
    

    
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
        max_length=3, choices=TYPE_DE_MALADIE_CHOICES, blank=True, null=True)

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
    
    