<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";

  import type { Questionnaire } from "./questionnaire";

  export let questionnaire: Questionnaire;

  export function getHighestKey(questionnaire: Questionnaire): number {
    return (
      questionnaire.reduce((key, section) => Math.max(key, section.id), 0) + 1
    );
  }
  let stepCount = getHighestKey(questionnaire);

  function addSection(idx: number) {
    const startIdx = idx + 1;

    stepCount += 1;

    questionnaire.splice(startIdx, 0, {
      id: stepCount,
      type: "section",
      title: "Hello",
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

  .section {
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
</style>

<main>
  <div class="sectionContainer">
    <div class="addSection">
      <button class="add" on:click={() => addSection(-1)}>Add Section</button>
    </div>
    <div
      use:dndzone={{ items: questionnaire, flipDurationMs, dropTargetStyle }}
      on:consider={handleDndConsider}
      on:finalize={handleDndFinalize}>
      {#each questionnaire as section, idx (section.id)}
        <div class="moveSection" animate:flip={{ duration: flipDurationMs }}>
          <div class="section">
            <p>Section {section.id}</p>

            <!-- <slot /> -->

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
