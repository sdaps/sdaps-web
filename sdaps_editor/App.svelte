<script lang="ts">
  let sections = [];
  let stepCount = 0;

  function addSection(idx: number) {
    const startIdx = idx + 1;

    stepCount += 1;

    sections.splice(startIdx, 0, {
      type: "section",
      idx: startIdx,
      step: stepCount,
    });

    for (let index = startIdx; index < sections.length; index++) {
      sections[index].idx = index;
    }

    sections = sections;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    sections.splice(startIdx, 1);

    for (let index = startIdx; index < sections.length; index++) {
      sections[index].idx = index;
    }

    sections = sections;
  }
</script>

<main>
  <h1>ASHTASHTASHTAS</h1>
  <ul>
    <li>
      <button class="btn btn-primary" on:click={() => addSection(-1)}>Add
        Section</button>
    </li>
    {#each sections as section (section.idx)}
      <li>
        <button class="btn" disabled>Section
          {section.idx}
          ({section.step})</button>
        <button
          class="btn btn-danger"
          on:click={() => deleteSection(section.idx)}>Remove</button>
      </li>
      <li>
        <button
          class="btn btn-primary"
          on:click={() => addSection(section.idx)}>Add Section</button>
      </li>
    {/each}
  </ul>
</main>
