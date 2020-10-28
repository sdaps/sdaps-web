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
  }

  .section {
    display: block;
  }
</style>

<main>
  <div class="sectionContainer">
    <div class="section">
      <button class="btn btn-primary" on:click={() => addSection(-1)}>Add
        Section</button>
    </div>
    {#each sections as section, idx (section.id)}
      <div class="section">
        <button class="btn" disabled>Section {section.id}</button>
        <button
          class="btn btn-danger"
          on:click={() => deleteSection(idx)}>Remove</button>
      </div>
      <div class="section">
        <button class="btn btn-primary" on:click={() => addSection(idx)}>Add
          Section</button>
      </div>
    {/each}
  </div>
</main>
