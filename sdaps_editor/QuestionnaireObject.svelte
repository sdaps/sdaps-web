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

  // Add and remove

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

  // Drag and drop

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
  }

  .questionnaireObject {
    display: block;
  }

  .addSection {
    display: block;
  }

  button {
    border: none;
  }

  button.add {
    width: 100%;
    border: none;
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
    <div class="addSection list-group-item list-group-item-action">
      <button class="add btn btn-sm btn-success" on:click={() => addSection(-1)}>Add {tool}</button>
    </div>
    <div
      use:dndzone={{ items: questionnaire, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' } }}
      on:consider={handleDndConsider}
      on:finalize={handleDndFinalize}>
      {#each questionnaire as questionnaireObject, idx (questionnaireObject.id)}
        <div class="moveSection list-group" animate:flip={{ duration: flipDurationMs }}>
          <div class="questionnaireObject list-group-item list-group-item-action">
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1"><span class="badge badge-dark">{questionnaireObject.type}</span></h6>
              <small>
                <button
                  class="remove btn btn-sm btn-outline-danger"
                  on:click={() => deleteSection(idx)}><i class="la la-trash"></i></button>
              </small>
            </div>
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
          </div>

          <div class="addSection list-group-item list-group-item-action">
            <button class="add btn btn-sm btn-success" on:click={() => addSection(idx)}>Add
              {tool}</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</main>
