<script lang="ts">
  import type { SectionQuestionnaireObject } from "../questionnaire";

  export let section: SectionQuestionnaireObject;
</script>

<div class="input-group mb-3">
  <div class="input-group-prepend">
    <span class="input-group-text" id="basic-addon3">Section Title</span>
  </div>
  <input type="text" class="form-control" bind:value={section.title} />
</div>
