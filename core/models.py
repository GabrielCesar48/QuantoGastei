from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Usuario customizado com campos extras.
    Estende o User padrão do Django.
    """
    PLANO_CHOICES = [
        ('free', 'Gratuito'),
        ('pro', 'Premium'),
    ]
    
    telefone = models.CharField(max_length=20, blank=True)
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True)
    plano = models.CharField(max_length=10, choices=PLANO_CHOICES, default='free')
    data_expiracao_pro = models.DateTimeField(null=True, blank=True)
    
    # Preferências do usuário
    dark_mode = models.BooleanField(default=False)
    notificacoes_ativas = models.BooleanField(default=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username}"
    
    @property
    def is_pro(self):
        """Verifica se o usuário tem plano PRO ativo."""
        if self.plano != 'pro':
            return False
        
        if self.data_expiracao_pro is None:
            return False
        
        from django.utils import timezone
        return timezone.now() < self.data_expiracao_pro