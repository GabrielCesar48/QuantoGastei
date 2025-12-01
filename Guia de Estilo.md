# 🎨 GUIA DE ESTILO - QuantoGastei

## Visão Geral

Design moderno, clean e funcional focado em facilitar o controle financeiro pessoal.

---

## 🎨 Paleta de Cores

### Cores Principais

```css
--primary: #6366F1         /* Indigo - Confiança, tecnologia, profissionalismo */
--primary-dark: #4F46E5
--primary-light: #818CF8
```

**Uso:** Headers, CTAs principais, elementos de destaque, navegação ativa

**Por que Indigo?**

* Transmite confiança e segurança (essencial para finanças)
* Moderno e tecnológico (diferente do verde tradicional)
* Não está associado a nenhum banco específico
* Visualmente agradável e não cansa a vista

---

### Cores Funcionais

#### ✅ Sucesso (Receitas)

```css
--success: #10B981         /* Verde Esmeralda */
--success-light: #D1FAE5
--success-dark: #059669
```

**Uso:** Valores de receitas, botões de adicionar receita, indicadores positivos

#### ❌ Erro (Despesas)

```css
--danger: #EF4444          /* Vermelho Coral */
--danger-light: #FEE2E2
--danger-dark: #DC2626
```

**Uso:** Valores de despesas, botões de adicionar despesa, alertas

#### ℹ️ Info (Transferências)

```css
--info: #3B82F6            /* Azul Céu */
--info-light: #DBEAFE
--info-dark: #2563EB
```

**Uso:** Transferências entre contas, informações neutras

---

### Escala de Cinzas

```css
--gray-50: #F9FAFB         /* Background secundário */
--gray-100: #F3F4F6        /* Hover states */
--gray-200: #E5E7EB        /* Borders */
--gray-300: #D1D5DB        /* Borders hover */
--gray-400: #9CA3AF
--gray-500: #6B7280        /* Texto secundário */
--gray-600: #4B5563
--gray-700: #374151
--gray-800: #1F2937
--gray-900: #111827        /* Texto principal */
```

---

## 📐 Tipografia

### Fontes

```css
--font-display: 'Plus Jakarta Sans'  /* Títulos, headings */
--font-body: 'Inter'                 /* Corpo, parágrafos, UI */
```

**Plus Jakarta Sans:** Moderna, geométrica, perfeita para títulos
**Inter:** Legível, otimizada para telas, excelente em tamanhos pequenos

### Escala de Tamanhos

```
12px (0.75rem)  - Texto pequeno, labels
14px (0.875rem) - Texto secundário, descrições
16px (1rem)     - Texto padrão do corpo
18px (1.125rem) - Texto destacado
20px (1.25rem)  - Subtítulos
24px (1.5rem)   - Títulos de seção
30px (1.875rem) - Títulos principais
36px (2.25rem)  - Display, hero titles
```

### Pesos

```
300 - Light (raramente usado)
400 - Regular (corpo de texto)
500 - Medium (labels, botões)
600 - Semibold (subtítulos, destaque)
700 - Bold (títulos, valores importantes)
800 - Extrabold (hero, display)
```

---

## 🔲 Espaçamentos

### Grid Base: 4px

```
4px   - Micro
8px   - Pequeno
12px  - Médio-pequeno
16px  - Médio
20px  - Médio-grande
24px  - Grande
32px  - Extra-grande
40px  - XXL
48px  - XXXL
```

### Aplicação

* **Padding interno de cards:** 16-20px
* **Gap entre elementos:** 8-12px
* **Margens entre seções:** 20-24px
* **Padding de botões:** 12-14px vertical, 20-24px horizontal

---

## 🔵 Border Radius

```css
--radius-sm: 8px      /* Inputs, tags pequenas */
--radius-md: 12px     /* Botões, cards pequenos */
--radius-lg: 16px     /* Cards principais */
--radius-xl: 20px     /* Modais, containers grandes */
--radius-full: 9999px /* Círculos perfeitos, pills */
```

**Filosofia:** Arredondamentos generosos para um visual moderno e amigável

---

## 🌑 Sombras

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
    Uso: Inputs, elementos sutis

--shadow: 0 1px 3px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)
    Uso: Cards padrão, elementos básicos

--shadow-md: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)
    Uso: Cards elevados, hover states

--shadow-lg: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)
    Uso: Modais, dropdowns, elementos flutuantes

--shadow-xl: 0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04)
    Uso: Popovers, elementos de maior destaque
```

---

## 🎯 Componentes Principais

### 1. Botões de Ação (Action Buttons)

**Características:**

* Grid de 3 colunas
* Ícone circular colorido + texto descritivo
* Border colorido conforme função
* Background gradiente sutil
* Hover: elevação + intensificação da borda

**Cores:**

* Receita: Verde (#10B981)
* Despesa: Vermelho (#EF4444)
* Transferência: Azul (#3B82F6)

### 2. Cards de Resumo

**Características:**

* Background branco
* Border sutil (#E5E7EB)
* Padding: 20px
* Border radius: 12-16px
* Shadow suave
* Hover: leve elevação

### 3. Selector de Contas

**Características:**

* Scroll horizontal sem barra
* Gap: 12px
* Cards com mín-width: 140px
* Border no active: cor primary + shadow
* Ícone + nome + saldo

### 4. Bottom Navigation

**Características:**

* 4 itens principais
* Ícone + label
* Active: cor primary
* Background branco + border-top
* Fixed bottom

---

## 🎭 Animações e Transições

### Timing Functions

```css
cubic-bezier(0.4, 0, 0.2, 1)  /* ease-out padrão */
ease                           /* transições simples */
linear                         /* loading spinners */
```

### Duração

```css
0.2s  - Micro-interações (hover, active)
0.3s  - Transições padrão (modais, slides)
0.5s  - Animações complexas (page transitions)
```

### Efeitos Comuns

```css
/* Hover em cards */
transform: translateY(-2px);
box-shadow: var(--shadow-md);

/* Hover em botões */
transform: translateY(-2px);

/* Active */
transform: translateY(0);

/* Slide de transações */
transform: translateX(4px);
```

---

## 📱 Responsividade

### Breakpoints

```css
max-width: 480px   /* Mobile (container principal) */
max-width: 768px   /* Tablet (futuro) */
max-width: 1024px  /* Desktop (futuro) */
```

### Mobile-First

* Container max-width: 480px
* Padding lateral: 20px (16px em telas <480px)
* Touch targets mínimos: 44x44px
* Botões grandes e espaçados

---

## 🌙 Dark Mode (Futuro)

### Paleta Dark

```css
--bg-primary: #1F2937       /* Background principal */
--bg-secondary: #111827     /* Background secundário */
--bg-card: #374151          /* Cards */
--text-primary: #F9FAFB     /* Texto principal */
--text-secondary: #D1D5DB   /* Texto secundário */
```

---

## ✨ Princípios de Design

### 1. **Clareza Visual**

* Hierarquia clara de informação
* Espaçamento generoso entre elementos
* Uso intencional de cor para direcionar atenção

### 2. **Consistência**

* Mesmos padrões em todo o app
* Componentes reutilizáveis
* Comportamentos previsíveis

### 3. **Acessibilidade**

* Contraste mínimo WCAG AA (4.5:1)
* Touch targets adequados (min 44px)
* Feedback visual claro

### 4. **Performance**

* Animações 60fps
* Transições suaves
* Loading states claros

### 5. **Modernidade**

* Design atual, não datado
* Elementos arredondados
* Shadows suaves
* Espaçamento generoso

---

## 🎨 Aplicação de Cores por Contexto

### Headers

* Background: Gradiente Primary
* Texto: Branco
* Border-radius: 0 0 24px 24px

### Cards de Valores

* Receitas: Texto verde
* Despesas: Texto vermelho
* Saldo: Texto primary (indigo)

### Ícones

* Primary: #6366F1
* Success: #10B981
* Danger: #EF4444
* Info: #3B82F6
* Neutral: #6B7280

### Backgrounds

* Página: #F9FAFB (gray-50)
* Cards: #FFFFFF
* Inputs: #FFFFFF
* Hover: #F3F4F6 (gray-100)

---

## 📋 Checklist de Implementação

✅ Cores definidas no CSS
✅ Fontes carregadas (Plus Jakarta Sans + Inter)
✅ Componentes principais estilizados
✅ Animações configuradas
✅ Responsividade mobile
⏳ Dark mode (futuro)
⏳ Temas customizáveis (futuro)

---

## 🎯 Diferencial Visual

### Em relação a outros apps financeiros:

1. **Menos poluído:** Espaços brancos generosos
2. **Mais moderno:** Indigo ao invés de verde tradicional
3. **Mais funcional:** Botões grandes e claros
4. **Mais agradável:** Gradientes sutis, sombras suaves

---

## 💡 Dicas de Uso

### Para Desenvolvedores:

* Use variáveis CSS para cores (var(--primary))
* Mantenha consistência nos border-radius
* Sempre adicione hover states
* Use as classes utilitárias do sistema

### Para Designers:

* Exporte assets em múltiplos tamanhos (@1x, @2x, @3x)
* Use a paleta de cores documentada
* Mantenha hierarquia visual clara
* Teste em dispositivos reais

---

**Versão:** 1.0

**Data:** Dezembro 2024

**Status:** Implementado ✅
