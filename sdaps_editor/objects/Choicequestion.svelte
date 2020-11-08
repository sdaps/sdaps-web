<script lang="ts">
  import type { ChoicequestionQuestionnaireObject } from "../questionnaire";
  import {
    InputGroup,
    InputGroupAddon,
    InputGroupText,
    Input,
    Button,
    CustomInput,
    CardBody,
  } from "sveltestrap";

  import { updateKey } from "../keyTracker";

  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";

  import { getHighestKey } from "../questionnaire";

  let mode: "choiceitem" | "choiceitemtext" = "choiceitem";

  export let choicequestion: ChoicequestionQuestionnaireObject;

  const key = getHighestKey(choicequestion.children);
  const listKey = updateKey(key);

  function createSubObject(type) {
    if (type === "choiceitemtext") {
      return { id: $listKey, type, colspan: 1, answer: "Answer", height: 2 };
    } else if (type === "choiceitem") {
      return { id: $listKey, type, colspan: 1, answer: "Answer" };
    }
  }

  // Add and remove
  function addSection(idx: number) {
    const startIdx = idx + 1;

    $listKey += 1;

    if (mode === "choiceitem") {
      choicequestion.children.splice(startIdx, 0, createSubObject(mode));
    } else if (mode === "choiceitemtext") {
      choicequestion.children.splice(startIdx, 0, createSubObject(mode));
    }
    choicequestion.children = choicequestion.children;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    choicequestion.children.splice(startIdx, 1);

    choicequestion.children = choicequestion.children;
  }

  const flipDurationMs = 50;

  function consider(e) {
    choicequestion.children = e.detail.items;
  }

  function finalize(e) {
    choicequestion.children = e.detail.items;
  }
</script>

<InputGroup>
  <InputGroupAddon addonType="prepend">
    <InputGroupText>Columns</InputGroupText>
  </InputGroupAddon>
  <Input
    placeholder="columns"
    type="number"
    bind:value={choicequestion.columns} />
</InputGroup>

<InputGroup>
  <InputGroupAddon addonType="prepend">
    <InputGroupText>Question</InputGroupText>
  </InputGroupAddon>
  <Input placeholder="question" bind:value={choicequestion.question} />
</InputGroup>

<details>
  <summary>Children</summary>

  <CustomInput type="select" bind:value={mode} id="mode" name="modeSelect">
    <option value="choiceitem">Choice Item</option>
    <option value="choiceitemtext">Choice Item Text</option>
  </CustomInput>

  <Button color="success" on:click={() => addSection(-1)}>
    Add groupaddchoice
  </Button>

  <div
    use:dndzone={{ items: choicequestion.children, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' }, type: 'choicequestion' }}
    on:consider={consider}
    on:finalize={finalize}>
    {#each choicequestion.children as child, idx (child.id)}
      <div animate:flip={{ duration: flipDurationMs }}>
        <CardBody>
          {#if child.type === 'choiceitem'}
            <InputGroup>
              <InputGroupAddon addonType="prepend">
                <InputGroupText>Colspan</InputGroupText>
              </InputGroupAddon>
              <Input
                placeholder="Colspan"
                type="number"
                min="1"
                step="1"
                bind:value={child.colspan} />
            </InputGroup>

            <InputGroup>
              <InputGroupAddon addonType="prepend">
                <InputGroupText>Answer</InputGroupText>
              </InputGroupAddon>
              <Input placeholder="Answer" bind:value={child.answer} />
            </InputGroup>

            <Button color="danger" on:click={() => deleteSection(idx)}>
              Remove
            </Button>
          {:else}
            <InputGroup>
              <InputGroupAddon addonType="prepend">
                <InputGroupText>Colspan</InputGroupText>
              </InputGroupAddon>
              <Input
                placeholder="Colspan"
                type="number"
                min="1"
                step="1"
                bind:value={child.colspan} />
            </InputGroup>

            <InputGroup>
              <InputGroupAddon addonType="prepend">
                <InputGroupText>Answer</InputGroupText>
              </InputGroupAddon>
              <Input placeholder="Answer" bind:value={child.answer} />
            </InputGroup>

            <InputGroup>
              <InputGroupAddon addonType="prepend">
                <InputGroupText>Height</InputGroupText>
              </InputGroupAddon>
              <Input
                placeholder="Height"
                type="number"
                min="1"
                step="1"
                bind:value={child.height} />
            </InputGroup>

            <Button color="danger" on:click={() => deleteSection(idx)}>
              Remove
            </Button>
          {/if}
        </CardBody>
      </div>
    {/each}
  </div>
</details>
