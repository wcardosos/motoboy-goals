# 🏍️ Corrida de Rua — Game Design Document

## Conceito

Jogo top-down onde o jogador é um motoboy que trabalha para aplicativos de entrega. O objetivo é completar corridas para cumprir metas financeiras pessoais (aluguel, contas, ajudar a família). Cada entrega é uma fase jogável onde o jogador precisa equilibrar velocidade, segurança no trânsito e integridade do pacote.

**Gênero:** Top-down driving / Simulação arcade
**Engine:** PyGame
**Perspectiva:** Câmera de cima acompanhando o jogador, rua rolando verticalmente (de cima pra baixo)

---

## Tema e Identidade

O jogo retrata a realidade do entregador de aplicativo no Brasil. Não é uma abordagem caricata — o tom é de respeito, mostrando os desafios reais (pressão de tempo, trânsito, dependência das avaliações, metas financeiras apertadas) dentro de uma experiência divertida e acessível.

---

## Controles

- **Setas ←→** — Mudar de faixa / desviar lateralmente
- **Seta ↑** — Acelerar
- **Seta ↓** — Frear / reduzir velocidade
- **Espaço** — Buzina (afasta alguns obstáculos como pedestres e cachorros)

---

## Mecânicas Principais

### 1. Pilotagem

A moto se move em uma via com 4 faixas. O jogador controla a velocidade (acelerar/frear) e a posição lateral (desviar entre faixas). A velocidade base é constante, mas o jogador pode acelerar pra ganhar tempo ou frear pra evitar problemas.

### 2. Saúde da Entrega

Barra visível no HUD que começa em 100%. Representa a integridade do pacote sendo entregue. Reduz quando:

- Passa rápido demais numa lombada (penalidade proporcional à velocidade)
- Colide com obstáculos (carros, buracos, cones)
- Faz desvios bruscos em alta velocidade

Se chegar a 0%, a entrega é cancelada automaticamente (pacote destruído).

### 3. Tempo de Entrega

Cada corrida tem um timer regressivo. Representa o prazo estimado pelo app. Entregar dentro do prazo garante pagamento completo. Cada segundo de atraso reduz o valor recebido. Atraso excessivo (ex: +60s) cancela a entrega.

### 4. Sistema de Avaliação (Estrelas)

No fim de cada entrega, o jogador recebe uma nota de 1 a 5 estrelas baseada em:

- ⏱️ Tempo de entrega (rápido = melhor)
- 📦 Saúde do pacote (mais intacto = melhor)

A média de estrelas acumulada afeta as corridas disponíveis: avaliação alta desbloqueia corridas que pagam mais; avaliação baixa limita as opções.

---

## Obstáculos e Elementos da Pista

### Obstáculos Fixos (sempre visíveis)
- **Lombadas** — Visíveis com antecedência. Se passar acima de certa velocidade, reduz saúde do pacote. Frear antes anula o dano.
- **Buracos** — Ocupam uma faixa. Desviar ou reduzir velocidade. Passar por cima em alta velocidade = dano grande no pacote e perda de velocidade.
- **Cones / Obras** — Bloqueiam uma faixa inteira, forçando desvio.

### Obstáculos Móveis (trânsito)
- **Carros lentos** — Ocupam uma faixa, andam devagar. O jogador precisa desviar ou esperar.
- **Carros rápidos (sentido contrário)** — Aparecem na faixa oposta em certos trechos, exigem reflexo.
- **Ônibus** — Grandes, ocupam mais espaço, param em pontos de ônibus bloqueando faixas temporariamente.
- **Caminhões** — Lentos e largos, difícil ultrapassar.

### Obstáculos Imprevisíveis
- **Pedestres atravessando** — Aparecem das laterais, o jogador precisa frear ou desviar. Atropelar = game over imediato.
- **Cachorros na rua** — Menores, se movem errático. Buzina afasta.

---

## Sistema Financeiro

### Fontes de Renda
- **Pagamento base** da entrega (fixo por corrida)
- **Bônus de tempo** (entregar antes do prazo)
- **Gorjeta** (proporcional às estrelas recebidas)

### Despesas e Objetivos
O jogo é dividido em dias. Cada dia o jogador pode fazer um número limitado de entregas (ex: 5-8 por dia). Ao final de um ciclo (ex: 7 dias), o jogador precisa ter acumulado dinheiro suficiente pra cobrir:

| Objetivo        | Valor     | Frequência  | Descrição                            |
|-----------------|-----------|-------------|--------------------------------------|
| Aluguel         | R$ 800    | Mensal      | Não pagar = game over                |
| Gasolina        | R$ 40/dia | Diário      | Sem gasolina = não pode fazer corrida|
| Manutenção moto | R$ 200    | Semanal     | Não pagar = moto mais lenta e frágil |
| Ajudar a mãe    | R$ 300    | Mensal      | Opcional, mas afeta narrativa        |

### Consequências
- Não pagar aluguel → Game over com mensagem narrativa
- Não pagar gasolina → Não pode jogar naquele dia (perde tempo)
- Não manter a moto → Velocidade máxima reduz, freia pior
- Ajudar a mãe → Desbloqueia diálogos e uma cena especial
- Comprar celular → Desbloqueia app de corrida premium (corridas que pagam mais)

---

## Fluxo do Jogo

```
[Tela Título]
     ↓
[Tela do Dia] — Mostra: dia atual, dinheiro, próximo objetivo, estado da moto
     ↓
[Seleção de Corrida] — 2 a 4 corridas disponíveis com:
   • Distância (curta/média/longa)
   • Pagamento base
   • Tipo de pacote (frágil paga mais, mas saúde reduz mais fácil)
     ↓
[Fase Jogável] — Corrida top-down com obstáculos
     ↓
[Tela de Resultado] — Estrelas, dinheiro ganho, saúde do pacote, infrações
     ↓
[Volta pra Tela do Dia] — Decide se faz mais corridas ou encerra o dia
     ↓
[Fim do Ciclo] — Paga contas, vê progresso, narrativa avança
```

---

## HUD (Interface durante a corrida)

```
┌─────────────────────────────────────────────┐
│  ⏱️ 02:34        📦 ████████░░ 78%          │
│                                             │
│  💰 R$ 12,50     ⚡ ████████████ (veloc.)   │
│                                             │
│           [área de jogo]                    │
│                                             │
│                  🏍️                         │
│                                             │
└─────────────────────────────────────────────┘
```

- **Timer** (canto superior esquerdo) — Tempo restante pra entrega
- **Saúde do Pacote** (canto superior direito) — Barra com porcentagem
- **Dinheiro acumulado no dia** (esquerda)

---

## Elementos Narrativos

O jogo não tem cutscenes longas, mas constrói narrativa através de:

- **Mensagens no celular** entre corridas — Mãe mandando mensagem, dono do AP cobrando, amigo pedindo empréstimo
- **Tela do dia** com frases do personagem — "Mais um dia. Se eu fizer 6 entregas consigo pagar a luz."
- **Eventos especiais** — Dia de chuva forte com texto "App mandou notificação: demanda alta, bônus de 50%. Mas a rua tá alagada."
- **Final** — Múltiplos fins baseados nas escolhas financeiras. Conseguiu pagar tudo e ajudar a mãe? Comprou o celular novo? Ou ficou preso no ciclo?

---

## Escopo da Demo (Apresentação)

Para a demo acadêmica, o escopo sugerido é:

1. **Tela título** com nome e controles
2. **Tela do dia** simplificada mostrando objetivo financeiro e dinheiro
3. **Seleção de corrida** com 2 opções (fácil e difícil)
4. **1 fase jogável completa** com: 4 faixas, carros, timer e barra de saúde do pacote
5. **Tela de resultado** com estrelas e dinheiro ganho
6. **Tela de fim de dia** mostrando se atingiu ou não o objetivo

Esse escopo é apresentável em 5-10 minutos de demonstração e mostra todas as mecânicas core do jogo.

---

## Identidade Visual (Sugestão)

- **Estilo pixel art simplificado**
- **Paleta** — Tons de asfalto (cinza escuro), amarelo de faixas, verde/vermelho dos semáforos, laranja dos coletes de motoboy
- **Câmera** — Top-down com leve inclinação (pseudo 3/4) para dar profundidade
- **Referência visual** — Estética de jogos retrô de corrida como "Road Fighter" (NES) mas com identidade urbana brasileira