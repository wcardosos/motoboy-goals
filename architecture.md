# Motoboy — Documentação de Arquitetura

## Visão Geral

Jogo top-down de motoboy em pygame. O jogador pilota uma moto por uma rodovia infinita de 4 faixas, desviando de veículos e obstáculos enquanto realiza entregas dentro do prazo e preservando a integridade do pacote.

O projeto segue uma **arquitetura em 4 camadas** com separação clara de responsabilidades: Core, Entities, Systems e UI.

---

## Arquitetura em Camadas

```
┌─────────────────────────────────────────────┐
│                   UI / HUD                  │  ← Renderiza informações (HUD, menus, telas)
├─────────────────────────────────────────────┤
│                  Systems                    │  ← Regras e lógica do jogo
├─────────────────────────────────────────────┤
│                  Entities                   │  ← Objetos do mundo (moto, carros, obstáculos)
├─────────────────────────────────────────────┤
│                   Core                      │  ← Motor do jogo (loop, cenas, input)
└─────────────────────────────────────────────┘
```

**Princípio de dependência:** cada camada conhece apenas a camada imediatamente abaixo. UI lê Systems, Systems manipulam Entities, Entities usam Core. Nenhuma camada referencia uma camada acima.

---

## Camada 1 — Core

Responsável pelo motor do jogo: loop principal, gerenciamento de cenas e captura de input.

### Game

Classe raiz da aplicação. Inicializa o pygame, mantém o clock e delega o controle para a cena ativa.

| Responsabilidade | Descrição |
|---|---|
| Inicialização | Configura display, clock, fonte padrão |
| Game Loop | Executa o ciclo input → update → render a cada frame |
| Gerenciamento de cena | Mantém a cena ativa e permite transições |
| Delta time | Calcula `dt` para movimentação frame-independent |

### SceneManager

Controla o fluxo entre as telas do jogo.

```
MenuScene → GameplayScene → DeliveryResultScene
                ↓                    ↓
           PauseScene          MenuScene (volta)
```

Cada cena implementa a interface:

```python
class Scene:
    def handle_event(self, event): ...
    def update(self, dt): ...
    def draw(self, screen): ...
```

### InputHandler

Abstrai a captura de input do pygame. Mapeia teclas para ações do jogo (`ACCELERATE`, `BRAKE`, `MOVE_LEFT`, `MOVE_RIGHT`, `PAUSE`), desacoplando a lógica do jogo das teclas físicas.

---

## Camada 2 — Entities

Objetos que existem no mundo do jogo. Seguem uma hierarquia baseada em herança com uma classe base `Entity`.

### Hierarquia de Classes

```
Entity
├── Vehicle
│   ├── Moto
│   ├── Car
│   └── Truck
│
├── Obstacle
│   ├── Hole
│   ├── Cone
│   └── SpeedBump
│
└── Road
```

### Entity (base)

Classe abstrata com os atributos e comportamentos comuns a tudo que existe na pista.

| Atributo | Tipo | Descrição |
|---|---|---|
| `x`, `y` | float | Posição no mundo |
| `width`, `height` | int | Dimensões do hitbox |
| `speed` | float | Velocidade vertical (px/s) |
| `sprite` | Surface | Imagem visual (placeholder = retângulo) |

| Método | Descrição |
|---|---|
| `update(dt)` | Atualiza posição e estado |
| `draw(screen)` | Renderiza na tela |
| `rect` → Rect | Retorna o hitbox para colisão |
| `is_off_screen()` → bool | Verifica se saiu da tela |

### Vehicle → Entity

Subclasse para objetos móveis na pista.

| Atributo Adicional | Tipo | Descrição |
|---|---|---|
| `lane` | int | Faixa atual (0–3) |
| `color` | tuple | Cor do veículo (até ter sprite real) |

#### Moto → Vehicle

Controlada pelo jogador. **Não conhece** o sistema de entregas (Opção A — "Moto burra").

| Atributo | Tipo | Descrição |
|---|---|---|
| `base_speed` | float | Velocidade constante da via |
| `current_speed` | float | Velocidade real (afetada por aceleração/freio) |
| `is_braking` | bool | Indica se o jogador está freando |

| Método | Descrição |
|---|---|
| `handle_input(actions)` | Processa ações mapeadas do InputHandler |
| `accelerate(dt)` | Incrementa velocidade até o máximo |
| `brake(dt)` | Reduz velocidade até o mínimo |
| `move_lateral(direction, dt)` | Move entre faixas suavemente |

#### Car → Vehicle

Obstáculo móvel padrão. Spawna no topo, desce na pista com velocidade variada.

| Atributo | Tipo | Descrição |
|---|---|---|
| `speed` | float | Aleatório entre `CAR_SPEED_MIN` e `CAR_SPEED_MAX` |

#### Truck → Vehicle

Veículo grande. Mais lento que carros, mas ocupa mais espaço horizontal, dificultando desvios.

| Atributo | Tipo | Descrição |
|---|---|---|
| `width` | int | Maior que Car (pode ocupar ~1.5 faixa) |
| `speed` | float | Menor que Car |

### Obstacle → Entity

Objetos estáticos (ou quase) na pista. Não mudam de faixa.

#### Hole → Obstacle

Buraco na pista. Causa dano ao pacote e pode causar perda momentânea de controle.

| Dano | Efeito extra |
|---|---|
| Médio-alto | Leve desvio involuntário na moto |

#### Cone → Obstacle

Obstáculo menor e mais frequente. Dano baixo ao pacote.

| Dano | Efeito extra |
|---|---|
| Baixo | Nenhum |

#### SpeedBump → Obstacle

Lombada. Penalidade **proporcional à velocidade** do jogador no momento do contato.

| Dano | Fórmula |
|---|---|
| Variável | `damage = base_damage * (moto.current_speed / moto.base_speed)` |

A lombada é o único obstáculo em que frear *antes* do contato é a estratégia correta, criando uma decisão interessante entre velocidade e segurança.

### Road

Gerencia o scroll infinito da rodovia. Usa duas cópias da superfície empilhadas verticalmente.

| Método | Descrição |
|---|---|
| `update(dt, speed)` | Move as duas superfícies para baixo; reposiciona ao sair da tela |
| `draw(screen)` | Desenha ambas as superfícies |

---

## Camada 3 — Systems

Módulos de lógica que implementam as regras do jogo. Cada system tem uma responsabilidade isolada. Manipulam Entities mas **não desenham nada**.

### CollisionSystem

Detecta colisões entre a moto e os demais objetos, despacha os efeitos para os systems responsáveis.

```
CollisionSystem.update()
  └── para cada entity na pista:
       se moto.rect.colliderect(entity.rect):
           ├── Vehicle → GameplayScene.trigger_crash()
           ├── Hole / Cone → DeliverySystem.apply_damage(amount)
           └── SpeedBump → DeliverySystem.apply_damage(f(moto.speed))
```

A moto não decide o que acontece na colisão — o CollisionSystem é quem resolve, consultando o tipo do obstáculo e delegando ao system correto.

### SpawnSystem

Controla quando e o quê aparece na pista.

| Responsabilidade | Descrição |
|---|---|
| Frequência | Intervalo entre spawns diminui com o tempo/distância |
| Distribuição | Define probabilidade de cada tipo (Car 50%, Truck 20%, Cone 15%, Hole 10%, SpeedBump 5%) |
| Segurança | Garante que não spawna obstáculos impossíveis de desviar (valida posição antes de confirmar) |

Parâmetros de spawn podem variar por nível de dificuldade da corrida.

### DeliverySystem

Gerencia o estado da entrega em andamento.

| Atributo | Tipo | Descrição |
|---|---|---|
| `package_health` | float | 0–100%. Saúde do pacote |
| `time_limit` | float | Tempo total em segundos |
| `time_remaining` | float | Timer regressivo |
| `payment_base` | float | Valor base da entrega |
| `is_active` | bool | Se há uma entrega em andamento |

| Método | Descrição |
|---|---|
| `start(delivery)` | Inicia uma nova entrega com parâmetros |
| `apply_damage(amount)` | Reduz saúde do pacote |
| `tick(dt)` | Decrementa o timer |
| `calculate_payment()` → float | Valor final com penalidades de atraso |
| `is_failed()` → bool | True se saúde = 0 ou atraso > 60s |
| `finish()` → DeliveryResult | Finaliza e retorna resultado |

**Regras de pagamento:**

```
se time_remaining >= 0:
    pagamento = payment_base
senão:
    atraso = abs(time_remaining)
    se atraso > 60: entrega cancelada, pagamento = 0
    senão: pagamento = payment_base * (1 - atraso / 60)
```

### RatingSystem

Calcula a avaliação por entrega e mantém a média acumulada.

| Método | Descrição |
|---|---|
| `calculate_stars(result)` → int | 1–5 estrelas baseado em tempo + saúde do pacote |
| `update_average(stars)` | Atualiza a média móvel |
| `get_available_tiers()` → list | Retorna os níveis de corrida desbloqueados |

**Cálculo de estrelas:**

| Critério | Peso |
|---|---|
| Tempo (% do prazo utilizado) | 50% |
| Saúde do pacote (% restante) | 50% |

```
score = (time_score * 0.5) + (health_score * 0.5)

5 estrelas: score >= 90%
4 estrelas: score >= 75%
3 estrelas: score >= 55%
2 estrelas: score >= 35%
1 estrela:  score < 35%
```

**Impacto da média:**

| Média | Corridas disponíveis |
|---|---|
| ≥ 4.5 | Premium (pagamento alto, prazo justo) |
| ≥ 3.5 | Standard + Express |
| ≥ 2.5 | Standard |
| < 2.5 | Apenas corridas básicas (pagamento mínimo) |

---

## Camada 4 — UI / HUD

Componentes visuais que leem dados dos Systems e renderizam na tela. Não contêm lógica de jogo.

### HUD (durante gameplay)

```
┌────────────────────────────────────────┐
│  ⏱️ 01:23        📦 ████████░░ 78%    │
│  ⭐ 4            💰 R$ 12,50          │
│                                        │
│            [ área do jogo ]            │
│                                        │
|                  │
└────────────────────────────────────────┘
```

| Elemento | Fonte de dados |
|---|---|
| Timer regressivo | `DeliverySystem.time_remaining` |
| Barra de saúde do pacote | `DeliverySystem.package_health` |
| Média de estrelas | `RatingSystem.average` |
| Valor da corrida | `DeliverySystem.payment_base` |

### DeliveryResultScreen

Tela exibida ao fim de cada entrega.

| Informação | Descrição |
|---|---|
| Estrelas recebidas | Animação de 1 a 5 estrelas |
| Saúde do pacote | % final |
| Tempo | Dentro do prazo ou atraso |
| Pagamento recebido | Valor final calculado |
| Média atualizada | Nova média de estrelas |

---

## Estrutura de Diretórios

```
motoboy-goals/
├── main.py                  # Entry point
├── core/
│   ├── game.py              # Classe Game (loop, init)
│   ├── scene.py             # Scene base + SceneManager
│   └── input_handler.py     # Mapeamento de teclas → ações
├── entities/
│   ├── entity.py            # Entity base
│   ├── vehicle.py           # Vehicle, Moto, Car, Truck
│   ├── obstacle.py          # Obstacle, Hole, Cone, SpeedBump
│   └── road.py              # Road (scroll infinito)
├── systems/
│   ├── collision.py         # CollisionSystem
│   ├── spawn.py             # SpawnSystem
│   ├── delivery.py          # DeliverySystem
│   └── rating.py            # RatingSystem
├── ui/
│   ├── hud.py               # HUD do gameplay
│   └── screens.py           # Menu, resultado, pause
├── scenes/
│   ├── menu_scene.py        # Tela inicial
│   ├── gameplay_scene.py    # Cena principal do jogo
│   ├── pause_scene.py       # Overlay de pausa
│   └── result_scene.py      # Resultado da entrega
├── config/
│   └── settings.py          # Constantes (tamanhos, velocidades, balanceamento)
└── assets/
    ├── sprites/
    └── sounds/
```

---

## Fluxo de uma Entrega (sequência simplificada)

```
1. MenuScene: jogador seleciona uma corrida disponível
       ↓
2. GameplayScene inicia:
   - DeliverySystem.start(delivery) → timer e saúde = 100%
   - SpawnSystem começa a gerar obstáculos
       ↓
3. Game loop a cada frame:
   - InputHandler captura ações
   - Moto.handle_input(actions) → move/acelera/freia
   - Road.update(dt, speed) → scroll
   - SpawnSystem.update(dt) → gera novos obstáculos
   - Todas entities.update(dt)
   - CollisionSystem.update() → detecta colisões → DeliverySystem.apply_damage()
   - DeliverySystem.tick(dt) → atualiza timer
   - HUD.draw() → renderiza estado atual
       ↓
4. Entrega encerra quando:
   - Moto chega ao destino (timer pode ou não ter expirado) OU
   - package_health = 0 (pacote destruído) OU
   - Atraso > 60s (cancelamento)
       ↓
5. DeliveryResultScene:
   - RatingSystem.calculate_stars(result)
   - Exibe pagamento, estrelas, saúde final
   - RatingSystem.update_average(stars)
       ↓
6. Volta ao MenuScene com novas corridas baseadas na média
```

---

## Decisões de Design

| Decisão | Justificativa |
|---|---|
| **Moto** | A moto não conhece o DeliverySystem. Colisões são resolvidas pelo CollisionSystem, que delega danos ao DeliverySystem. Isso mantém as responsabilidades separadas e facilita adicionar mecânicas futuras (power-ups, tipos de entrega) sem alterar a Moto. |
| **Systems como módulos isolados** | Cada mecânica (colisão, spawn, entrega, avaliação) é um system independente. Facilita testes, debug e evolução individual de cada regra. |
| **Scene como interface** | Cenas são intercambiáveis com a mesma interface (handle_event, update, draw). Adicionar novas telas (loja, garagem, ranking) exige zero alteração no Core. |
| **SpeedBump com dano variável** | Cria uma decisão de gameplay significativa: o jogador precisa escolher entre manter velocidade (ganhar tempo, arriscar o pacote) ou frear (perder tempo, proteger o pacote). |
| **Config centralizado** | Todas as constantes de balanceamento ficam em `settings.py`, facilitando ajustes sem caçar números mágicos no código. |