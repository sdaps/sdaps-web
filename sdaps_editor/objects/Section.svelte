<script lang="ts">
  import type { SectionQuestionnaireObject } from "../questionnaire";

  export let section: SectionQuestionnaireObject;
</script>

<label>Section Title: <input type="text" bind:value={section.title} /></label>
