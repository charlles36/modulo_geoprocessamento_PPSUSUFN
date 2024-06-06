from django.db import models

from django.utils.text import slugify

class CorrecaoBairro(models.Model):
    bairro_incorreto = models.CharField(max_length=100, unique=True)
    bairro_correto = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.nome_incorreto} -> {self.nome_correto}'

class Relatorio(models.Model):
    data = models.DateField(unique=True)
    relatorio = models.FileField(upload_to='relatorios')

    def save(self, *args, **kwargs):
        if not self.id:  # Renomear apenas na criação
            data_str = self.data.strftime('%Y-%m-%d')
            extensao = self.relatorio.name.split('.')[-1]
            novo_nome = f"{data_str}.{extensao}"
            self.relatorio.name = novo_nome
        super().save(*args, **kwargs)

class Casos(models.Model):
    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, default=1)
    bairro = models.CharField(max_length=100)
    cid = models.CharField(max_length=100)
    descricao_cid = models.CharField(max_length=200)
    quantidade_casos = models.IntegerField()
    data = models.DateField()

