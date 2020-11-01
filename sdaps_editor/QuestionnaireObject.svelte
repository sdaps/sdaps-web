<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { createQuestionnaireObject } from "./factory";
  import { updateKey } from "./keyTracker";

  import type { Questionnaire, QuestionnaireObject } from "./questionnaire";
  import { getHighestKey } from "./questionnaire";

  import Textbody from "./objects/Textbody.svelte";
  import Textbox from "./objects/Textbox.svelte";
  import Section from "./objects/Section.svelte";
  import Singlemark from "./objects/Singlemark.svelte";
  import Markgroup from "./objects/Markgroup.svelte";

  export let questionnaire: Questionnaire;

  const stepCount = getHighestKey(questionnaire);
  const listKey = updateKey(stepCount);

  let tool: QuestionnaireObject["type"] = "section";

  function addSection(idx: number) {
    const startIdx = idx + 1;

    $listKey += 1;

    questionnaire.splice(
      startIdx,
      0,
      createQuestionnaireObject(tool, $listKey)
    );

    questionnaire = questionnaire;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    questionnaire.splice(startIdx, 1);

    questionnaire = questionnaire;
  }

  const flipDurationMs = 50;

  function handleDndConsider(e) {
    questionnaire = e.detail.items;
  }

  function handleDndFinalize(e) {
    questionnaire = e.detail.items;
  }
</script>

<style>
  .sectionContainer {
    display: flex;
    flex-flow: column;

    width: 100%;
    border: solid 1px black;
  }

  .questionnaireObject {
    display: block;
    border: solid 1px black;
  }

  .addSection {
    display: block;
    border: solid 1px black;
  }

  button {
    border: none;
  }

  button.remove {
    background-color: #ef2929;
    color: white;
    font-weight: bold;
  }

  button.add {
    width: 100%;
    border: none;
    background-color: #8ae234;
  }

  .moveSection {
    background-color: white;
  }

  .toolbox {
    display: block;
    position: sticky;
    top: 0;
    border: solid 1px black;
    background-color: antiquewhite;
    margin-bottom: 1em;
    box-shadow: 0px 10px 13px -7px black, 5px 5px 15px 5px rgba(0, 0, 0, 0);
  }
</style>

<main>
  <div class="toolbox">
    <input
      type="radio"
      id="section"
      name="tool"
      value="section"
      bind:group={tool} />
    <label for="section">Section</label>

    <input
      type="radio"
      id="textbody"
      name="tool"
      value="textbody"
      bind:group={tool} />
    <label for="textbody">Textbody</label>

    <input
      type="radio"
      id="textbox"
      name="tool"
      value="textbox"
      bind:group={tool} />
    <label for="textbox">Textbox</label>

    <input
      type="radio"
      id="singlemark"
      name="tool"
      value="singlemark"
      bind:group={tool} />
    <label for="singlemark">Singlemark</label>

    <input
      type="radio"
      id="markgroup"
      name="tool"
      value="markgroup"
      bind:group={tool} />
    <label for="markgroup">Markgroup</label>
  </div>
  <div class="sectionContainer">
    <div class="addSection">
      <button class="add" on:click={() => addSection(-1)}>Add {tool}</button>
    </div>
    <div
      use:dndzone={{ items: questionnaire, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' } }}
      on:consider={handleDndConsider}
      on:finalize={handleDndFinalize}>
      {#each questionnaire as questionnaireObject, idx (questionnaireObject.id)}
        <div class="moveSection" animate:flip={{ duration: flipDurationMs }}>
          <div class="questionnaireObject">
            {#if questionnaireObject.type == 'textbody'}
              <Textbody bind:textbody={questionnaireObject} />
            {:else if questionnaireObject.type == 'textbox'}
              <Textbox bind:textbox={questionnaireObject} />
            {:else if questionnaireObject.type == 'section'}
              <Section bind:section={questionnaireObject} />
            {:else if questionnaireObject.type == 'singlemark'}
              <Singlemark bind:singlemark={questionnaireObject} />
            {:else if questionnaireObject.type == 'markgroup'}
              <Markgroup bind:markgroup={questionnaireObject} />
            {/if}

            <button
              class="remove"
              on:click={() => deleteSection(idx)}>Remove</button>
          </div>
          <div class="addSection">
            <button class="add" on:click={() => addSection(idx)}>Add
              {tool}</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</main>
