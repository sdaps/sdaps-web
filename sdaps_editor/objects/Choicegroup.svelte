<script lang="ts">
  import { updateKey } from "../keyTracker";

  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";

  import {
    InputGroup,
    InputGroupAddon,
    InputGroupText,
    Input,
    Button,
  } from "sveltestrap";
  import { partition } from "lodash";

  import type {
    ChoicegroupQuestionnaireObject,
    InnerGroupAddChoice,
    InnerChoiceLine,
  } from "../questionnaire";
  import { getHighestKey } from "../questionnaire";

  // TODO: Add kwargs

  export let choicegroup: ChoicegroupQuestionnaireObject;

  const key = getHighestKey(choicegroup.children);
  const listKey = updateKey(key);

  let [groupAddChoice, choiceLine] = partition(
    choicegroup.children,
    (item) => item.type === "groupaddchoice"
  );

  $: {
    choicegroup.children = groupAddChoice.concat(choiceLine);
  }

  function createSubObject(type: "groupaddchoice"): InnerGroupAddChoice;
  function createSubObject(type: "choiceline"): InnerChoiceLine;
  function createSubObject(
    type: "groupaddchoice" | "choiceline"
  ): InnerGroupAddChoice | InnerChoiceLine;
  function createSubObject(type) {
    if (type === "groupaddchoice") {
      return { id: $listKey, type, choice: "Choice" };
    } else if (type === "choiceline") {
      return { id: $listKey, type, question: "Question" };
    }
  }

  // Add and remove
  function addSection(idx: number, mode: "groupaddchoice" | "choiceline") {
    const startIdx = idx + 1;

    $listKey += 1;

    if (mode === "groupaddchoice") {
      groupAddChoice.splice(startIdx, 0, createSubObject(mode));

      groupAddChoice = groupAddChoice;
    } else if (mode === "choiceline") {
      choiceLine.splice(startIdx, 0, createSubObject(mode));

      choiceLine = choiceLine;
    }
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    choicegroup.children.splice(startIdx, 1);

    choicegroup.children = choicegroup.children;
  }

  // Drag and drop

  const flipDurationMs = 50;

  function handleGroupaddchoiceDndConsider(e) {
    groupAddChoice = e.detail.items;
  }

  function handleGroupaddchoiceDndFinalize(e) {
    groupAddChoice = e.detail.items;
  }

  function handleChoiceLineDndConsider(e) {
    choiceLine = e.detail.items;
  }

  function handleChoiceLineDndFinalize(e) {
    choiceLine = e.detail.items;
  }
</script>

<InputGroup>
  <InputGroupAddon addonType="prepend">
    <InputGroupText>Heading:</InputGroupText>
  </InputGroupAddon>
  <Input placeholder="heading" bind:value={choicegroup.heading} />
</InputGroup>

<details>
  <summary>Children</summary>

  <Button color="success" on:click={() => addSection(-1, 'groupaddchoice')}>
    Add groupaddchoice
  </Button>
  <div
    use:dndzone={{ items: groupAddChoice, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' }, type: 'groupaddchoice' }}
    on:consider={handleGroupaddchoiceDndConsider}
    on:finalize={handleGroupaddchoiceDndFinalize}>
    {#each groupAddChoice as child (child.id)}
      <div animate:flip={{ duration: flipDurationMs }}>
        {#if child.type === 'groupaddchoice'}
          <InputGroup>
            <InputGroupAddon addonType="prepend">
              <InputGroupText>Choice:</InputGroupText>
            </InputGroupAddon>
            <Input placeholder="Choice" bind:value={child.choice} />
          </InputGroup>
        {/if}
      </div>
    {/each}
  </div>

  <Button color="success" on:click={() => addSection(-1, 'choiceline')}>
    Add choiceline
  </Button>
  <div
    use:dndzone={{ items: choiceLine, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' }, type: 'choiceline' }}
    on:consider={handleChoiceLineDndConsider}
    on:finalize={handleChoiceLineDndFinalize}>
    {#each choiceLine as child (child.id)}
      <div animate:flip={{ duration: flipDurationMs }}>
        {#if child.type === 'choiceline'}
          <InputGroup>
            <InputGroupAddon addonType="prepend">
              <InputGroupText>Question:</InputGroupText>
            </InputGroupAddon>
            <Input placeholder="Question" bind:value={child.question} />
          </InputGroup>
        {/if}
      </div>
    {/each}
  </div>
</details>
