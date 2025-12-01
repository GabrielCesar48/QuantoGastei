from django.db import models
from django.conf import settings

class Conta(models.Model):
    """
    Representa uma conta financeira do usuário.
    Ex: Dinheiro, Cartão Nubank, Poupança, etc.
    """
    TIPO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('conta_corrente', 'Conta Corrente'),
        ('poupanca', 'Poupança'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('investimento', 'Investimento'),
        ('outro', 'Outro'),
    ]
    
    ICONE_CHOICES = [
        ('wallet', 'Carteira'),
        ('credit_card', 'Cartão'),
        ('account_balance', 'Banco'),
        ('savings', 'Poupança'),
        ('trending_up', 'Investimento'),
        ('payments', 'Pagamento'),
    ]
    
    COR_CHOICES = [
        ('#12A454', 'Verde'),
        ('#3B82F6', 'Azul'),
        ('#8B5CF6', 'Roxo'),
        ('#F59E0B', 'Laranja'),
        ('#EF4444', 'Vermelho'),
        ('#6B7280', 'Cinza'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contas'
    )
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Visual
    icone = models.CharField(max_length=30, choices=ICONE_CHOICES, default='wallet')
    cor = models.CharField(max_length=7, choices=COR_CHOICES, default='#12A454')
    
    # Controle
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['-ativa', 'nome']
        unique_together = ['usuario', 'nome']  # Evita nomes duplicados por usuário
    
    def __str__(self):
        return f"{self.nome}"
    
    @property
    def saldo_atual(self):
        """Calcula saldo atual: saldo_inicial + receitas - despesas."""
        from transacoes.models import Transacao
        
        receitas = Transacao.objects.filter(
            conta_origem=self,
            tipo='receita'
        ).aggregate(total=models.Sum('valor'))['total'] or 0
        
        despesas = Transacao.objects.filter(
            conta_origem=self,
            tipo='despesa'
        ).aggregate(total=models.Sum('valor'))['total'] or 0
        
        transferencias_enviadas = Transacao.objects.filter(
            conta_origem=self,
            tipo='transferencia'
        ).aggregate(total=models.Sum('valor'))['total'] or 0
        
        transferencias_recebidas = Transacao.objects.filter(
            conta_destino=self,
            tipo='transferencia'
        ).aggregate(total=models.Sum('valor'))['total'] or 0
        
        return (
            self.saldo_inicial 
            + receitas 
            - despesas 
            - transferencias_enviadas 
            + transferencias_recebidas
        )