<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { createQuestionnaireObject } from "./factory";

  import type { Questionnaire } from "./questionnaire";
  import { getHighestKey } from "./questionnaire";

  import Textbody from "./objects/Textbody.svelte";
  import Textbox from "./objects/Textbox.svelte";
  import Section from "./objects/Section.svelte";
  import Singlemark from "./objects/Singlemark.svelte";

  export let questionnaire: Questionnaire;

  let stepCount = getHighestKey(questionnaire);

  function addSection(idx: number) {
    const startIdx = idx + 1;

    stepCount += 1;

    questionnaire.splice(startIdx, 0, {
      id: stepCount,
      type: "textbox",
      expand: false,
      height: 12,
      question: "What?",
    });

    questionnaire = questionnaire;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    questionnaire.splice(startIdx, 1);

    questionnaire = questionnaire;
  }

  const flipDurationMs = 50;

  let dropTargetStyle;
  function handleDndConsider(e) {
    questionnaire = e.detail.items;

    dropTargetStyle = {
      outline: "solid 2px blue",
    };
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
    position: -webkit-sticky; /* Safari */
    position: sticky;
    top: 0;
    border: solid 1px black;
    margin-bottom: 1em;
  }
</style>

<main>
  <div class="toolbox">
    Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox
    Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox Toolbox
    Toolbox Toolbox Toolbox Toolbox Toolbox
  </div>
  <div class="sectionContainer">
    <div class="addSection">
      <button class="add" on:click={() => addSection(-1)}>Add Section</button>
    </div>
    <div
      use:dndzone={{ items: questionnaire, flipDurationMs, dropTargetStyle }}
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
            {/if}

            <button
              class="remove"
              on:click={() => deleteSection(idx)}>Remove</button>
          </div>
          <div class="addSection">
            <button class="add" on:click={() => addSection(idx)}>Add Section</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</main>
