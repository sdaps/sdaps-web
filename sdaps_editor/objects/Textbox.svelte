<script lang="ts">
  import type { TextboxQuestionnaireObject } from "../questionnaire";

  export let textbox: TextboxQuestionnaireObject;
</script>

<div class="input-group mb-3">
  <div class="input-group-prepend">
    <label class="input-group-text">Question:</label>
  </div>
  <input class="form-control" type="text" bind:value={textbox.question} />
  <div class="col-auto my-1">
    <div class="form-check">
      <input class="form-check-input" type="checkbox" bind:checked={textbox.expand} id="autoSizingCheck2">
      <label class="form-check-label" for="autoSizingCheck2">
      Expand
      </label>
    </div>
  </div>
  <div class="input-group-prepend">
    <span class="input-group-text">Height</span>
  </div>
<input class="form-control"
    type="number"
    min="1"
    max="12"
    step="1"
    disabled={textbox.expand}
    bind:value={textbox.height} />
</div>

<div class="input-group">
  <div class="input-group-prepend">
    <label class="input-group-text">Textbox Size:</label>
  </div>
  <textarea class="form-control" disabled={textbox.expand} aria-label="With textarea" bind:value={textbox.height}></textarea>
</div>
