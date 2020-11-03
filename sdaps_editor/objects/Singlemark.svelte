<script lang="ts">
  import type { SinglemarkQuestionnaireObject } from "../questionnaire";

  export let singlemark: SinglemarkQuestionnaireObject;
</script>
<div class="input-group mb-3">
  <div class="input-group-prepend">
    <label class="input-group-text" for="inputGroupSelect01">Question:</label>
  </div>
  <input type="text" class="form-control" placeholder="" aria-label="Example text with button addon" bind:value={singlemark.question} />
  <div class="input-group-prepend">
    <label class="input-group-text">Number of checkboxes:</label>
  </div>
  <input class="form-control"
    type="number"
    min="2"
    max="10"
    step="1"
    bind:value={singlemark.checkboxcount} />
</div>
<div class="input-group mb-3">
  <div class="input-group-prepend">
    <label class="input-group-text" for="inputGroupSelect01">Lower:</label>
  </div>
  <input class="form-control" placeholder="" aria-label="Example text with button addon" type="text" bind:value={singlemark.lower} />
  <div class="input-group-prepend">
    <label class="input-group-text" for="inputGroupSelect01">Upper:</label>
  </div>
  <input class="form-control" placeholder="" aria-label="Example text with button addon" type="text" bind:value={singlemark.upper} />
</div>

