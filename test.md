# Prompt para Evolução do App — "Prompt Library" Customizável (Modelo /)

**Contexto:**  
Inspirado na imagem.png da "Prompt Library" (LeetCode, Bullets, Study, etc.), a tarefa é implementar uma funcionalidade semelhante, permitindo ao usuário navegar, selecionar, criar, editar e usar prompts personalizados para IA no app.

---

## Objetivo da Feature

Permitir ao usuário gerenciar uma biblioteca de prompts (templates de configuração para IA), incluindo:
- Seleção de persona, instruções, tipo de tarefa e formatação do output.
- Criação, edição e exclusão de prompts próprios.
- Utilização de prompt builder/agente para facilitar criação de prompts otimizados por engenharia de prompt.

---

## Engenharia de Prompt — Estrutura Recomendada

### Exemplo de Estrutura de Prompt ("Prompt Template")

```yaml
persona: "Você é um assistente de entrevistas LeetCode em tempo real. Siga as seguintes regras estritamente."
task: 
  - "Responda perguntas de algoritmos de programação de forma rigorosa."
  - "Forneça instruções passo a passo se solicitado."
instructions:
  - "**Uso estrito de linguagem**: Não utilize meta-comentários, não mencione 'sua pergunta', não resuma a não ser solicitado."
  - "**Padrão de Output**: Seja detalhado, preciso, utilize Markdown, responda no idioma do usuário."
  - "**Gestão de intenção**: Se não houver clareza, destaque a ambiguidade de forma explícita."
output_format: "Markdown"
editable: true
tags: ["coding", "interview", "step-by-step"]
```

---

Outro exemplo que vc pode organizar:
"Você é um tutor socrático de Ciência da Computação. Nunca dê a resposta direta, faça perguntas que levem o aluno a pensar."

### Exemplo de Prompt Personalizado

#### Persona Prompt — UX Design Reviewer

```yaml
persona: "Você é um especialista em UX Design moderno focado em acessibilidade e interfaces conversacionais."
task: 
  - "Analise e sugira melhorias em fluxos de interface apontados."
instructions:
  - "Apresente recomendações de forma objetiva, fundamentada em heurísticas."
  - "Indique se há ambiguidade ou dependências externas."
output_format: "Bullet points com trechos explicativos em Markdown."
editable: true
tags: ["ux", "review", "accessibility"]
```

---

### Exemplo para Usuário Criar Seu Próprio

```yaml
persona: "Defina aqui o 'personagem' ou especialização da IA (ex: especialista em RH, coach, advogado)."
task: 
  - "Descreva a missão principal do assistente (ex: responder dúvidas trabalhistas, sugerir melhorias em documentos, criar argumentos)."
instructions:
  - "Insira regras específicas de conduta, estilo, respostas, palavras proibidas, formato preferencial, etc."
output_format: "Formato desejado: texto corrido, bullet points, tabelas Markdown, etc."
editable: true
tags: ["tema 1", "tema 2", "custom"]
```

---

## Funcionalidade Esperada

- **Prompt Library customizável** acessível direto na interface do app (menu lateral, janela pop-up, ou componente fixo).
- Lista de prompts built-in (ex: LeetCode, Sales, UX) e prompts pessoais do usuário.
- **Editor de Prompt** para criar ou modificar templates (preset) com campos: Persona, Task, Instructions, Output.
- Possibilidade de exportar/importar prompts (ex: arquivo YAML/JSON).
- Tags para facilitar busca/agrupamento.
- Feedback visual do prompt ativo e das instruções geradas para IA.
- Interação imediata com IA usando o prompt selecionado.
- Esses prompts devem ser salvo no banco de dados 
- A análise de imagem deve ser guiada pelo prompt ativo na "Prompt Library", permitindo ao usuário personalizar o tipo, a profundidade e a linguagem da análise.
 Usuário clica para analisar imagem.
   - O prompt gerado para enviar à IA é composto pelas seções do template ativo (Persona, Task, Instructions, Output).  
   - Se não houver prompt ativo, use o template padrão.

---

## Prompt Engenharia Avançada: Sugestão para Sistema

**Prompt Builder Agent**

Gerencie a criação/editoração de prompts conforme a estrutura abaixo, auxiliando o usuário na escolha/revisão dos elementos:

```markdown
[Prompt Builder]
1. **Persona**: Quem será a IA nessa interação? (Exemplo: especialista, professor, reviewer, brainstormer)
2. **Task**: O que ela deve resolver/fazer? (Objetivo central claro)
3. **Instructions**: Como ela deve responder? (Regras, formato, linguagem, restrições)
4. **Output**: Como será a saída? (Markdown, bullet points, resumo, tabela, estrutura etc.)
5. **Tags**: Palavras-chave para pesquisar depois

*Você pode adicionar múltiplos prompts, editar ou ativar/desativar conforme o contexto da sua reunião ou entrevista.*
```

---

## Referências e Inspiração

- Prompt Library do / ([imagem.png](imagem.png))
- Prompt Engineering best-practices: Persona/Task/Instructions/Output
- Customização dinâmica para IA conversacional

---

**Crie a biblioteca, editor e fluxo de prompts conforme acima, habilitando o usuário para criar experiências IA sob medida para diferentes contextos de reuniões, entrevistas ou tarefas em tempo real.**
