from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import sendTransaction
import hashlib


class Energy(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    produced_energy_in_watt = models.CharField(max_length=32, default=0, null=True)
    consumed_energy_in_watt = models.CharField(max_length=32, default=0, null=True)
    hash = models.CharField(max_length=32, default=None, null=True)
    txId = models.CharField(max_length=66, default=None, null=True)

    def __str__(self):
        return str(self.date)
# we enter the data within the ETH transaction if they have not already been entered
    def writeOnETH(self):
        if self.hash is not None:
            return None
        else:
            produced_consumed_energy_in_watt = f"Produced Energy in Watt: {self.produced_energy_in_watt} \n " \
                                               f"Consumed Energy in Watt: {self.consumed_energy_in_watt}."
            self.hash = hashlib.sha256(produced_consumed_energy_in_watt.encode('utf-8')).hexdigest()
            self.txId = sendTransaction(self.hash)
            self.save()
# we set a trigger, when the data is received we automatically start the WriteOnEth function
@receiver(post_save, sender=Energy)
def trigger(sender, instance, created, **kwargs):
    instance.writeOnETH()