from django.db import models
from django.conf import settings
from django.utils import timezone

class Assinatura(models.Model):
    """
    Controla assinaturas PRO dos usuários.
    Integração com Google Play Billing.
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
        ('pendente', 'Pendente'),
    ]
    
    PLANO_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assinaturas'
    )
    
    plano = models.CharField(max_length=10, choices=PLANO_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    
    # Dados do Google Play Billing
    purchase_token = models.CharField(max_length=500, unique=True, blank=True, null=True)
    product_id = models.CharField(max_length=100, blank=True)
    order_id = models.CharField(max_length=100, blank=True)
    
    # Datas
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    data_cancelamento = models.DateTimeField(null=True, blank=True)
    
    # Controle
    renovacao_automatica = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_plano_display()} ({self.status})"
    
    @property
    def esta_ativa(self):
        """Verifica se assinatura está ativa e não expirada."""
        return self.status == 'ativa' and timezone.now() < self.data_expiracao
    
    def cancelar(self):
        """Cancela a assinatura."""
        self.status = 'cancelada'
        self.data_cancelamento = timezone.now()
        self.renovacao_automatica = False
        self.save()


class LogPagamento(models.Model):
    """
    Log de eventos de pagamento (webhooks do Google)
    """
    assinatura = models.ForeignKey(
        Assinatura,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )
    
    evento = models.CharField(max_length=100)
    payload = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Pagamento'
        verbose_name_plural = 'Logs de Pagamento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.evento} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"