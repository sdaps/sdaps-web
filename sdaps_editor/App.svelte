<script lang="ts">
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
    {#each sections as section, idx (section.id)}
      <div class="section">
        <p>Section {section.id}</p>
        <button on:click={() => deleteSection(idx)}>Remove</button>
      </div>
      <div class="addSection">
        <button class="add" on:click={() => addSection(idx)}>Add Section</button>
      </div>
    {/each}
  </div>
</main>
