<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";

  let sections = [];
  let stepCount = 0;

  function addSection(idx: number) {
    const startIdx = idx + 1;

    stepCount += 1;

    sections.splice(startIdx, 0, {
      id: stepCount,
      type: "section",
    });

    sections = sections;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    sections.splice(startIdx, 1);

    sections = sections;
  }

  const flipDurationMs = 50;

  function handleDndConsider(e) {
    sections = e.detail.items;
  }

  function handleDndFinalize(e) {
    sections = e.detail.items;
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

    padding: 0.6em;
  }

  .addSection {
    display: block;
    border: solid 1px black;
  }

  button {
    border: solid 1px black;
  }

  button.add {
    width: 100%;
    border: none;
  }
</style>

<main>
  <div class="sectionContainer">
    <div class="addSection">
      <button class="add" on:click={() => addSection(-1)}>Add Section</button>
    </div>
    <div
      use:dndzone={{ items: sections, flipDurationMs }}
      on:consider={handleDndConsider}
      on:finalize={handleDndFinalize}>
      {#each sections as section, idx (section.id)}
        <div animate:flip={{ duration: flipDurationMs }}>
          <div class="section">
            <p>Section {section.id}</p>
            <button on:click={() => deleteSection(idx)}>Remove</button>
          </div>
          <div class="addSection">
            <button class="add" on:click={() => addSection(idx)}>Add Section</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
</main>
