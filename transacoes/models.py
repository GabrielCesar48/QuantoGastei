from django.db import models
from django.conf import settings

class Categoria(models.Model):
    """
    Categorias para organizar transações.
    Ex: Alimentação, Transporte, Lazer, Salário, etc.
    """
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]
    
    ICONE_CHOICES = [
        ('restaurant', 'Alimentação'),
        ('local_gas_station', 'Combustível'),
        ('directions_bus', 'Transporte'),
        ('home', 'Moradia'),
        ('shopping_cart', 'Compras'),
        ('medical_services', 'Saúde'),
        ('school', 'Educação'),
        ('sports_esports', 'Lazer'),
        ('checkroom', 'Vestuário'),
        ('work', 'Trabalho'),
        ('attach_money', 'Salário'),
        ('trending_up', 'Investimento'),
        ('card_giftcard', 'Presente'),
        ('more_horiz', 'Outros'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categorias',
        null=True,
        blank=True
    )
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    icone = models.CharField(max_length=30, choices=ICONE_CHOICES, default='more_horiz')
    cor = models.CharField(max_length=7, default='#6B7280')
    
    # Se usuario=None, é categoria padrão do sistema
    padrao = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['tipo', 'nome']
        unique_together = ['usuario', 'nome', 'tipo']
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    
class Transacao(models.Model):
    """
    Registro de movimentação financeira.
    Pode ser: Receita, Despesa ou Transferência.
    """
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
        ('transferencia', 'Transferência'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transacoes'
    )
    
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    
    conta_origem = models.ForeignKey(
        'contas.Conta',
        on_delete=models.PROTECT,
        related_name='transacoes_saida'
    )
    
    conta_destino = models.ForeignKey(
        'contas.Conta',
        on_delete=models.PROTECT,
        related_name='transacoes_entrada',
        null=True,
        blank=True
    )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='transacoes',
        null=True,
        blank=True
    )
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()
    
    observacoes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data', '-created_at']
        indexes = [
            models.Index(fields=['usuario', '-data']),
            models.Index(fields=['tipo', 'data']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} (R$ {self.valor})"
    
    def clean(self):
        """Validações customizadas."""
        from django.core.exceptions import ValidationError
        
        # Transferência deve ter conta destino
        if self.tipo == 'transferencia' and not self.conta_destino:
            raise ValidationError('Transferência precisa ter conta de destino.')
        
        # Transferência não pode ser da mesma conta
        if self.tipo == 'transferencia' and self.conta_origem == self.conta_destino:
            raise ValidationError('Não pode transferir para a mesma conta.')
        
        # Receita e Despesa não devem ter conta destino
        if self.tipo in ['receita', 'despesa'] and self.conta_destino:
            raise ValidationError(f'{self.get_tipo_display()} não deve ter conta de destino.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)