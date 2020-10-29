<script lang="ts">
  import QuestionnaireObject from "./QuestionnaireObject.svelte";

  const basePath = window.location.pathname;

  const questionnairePath = `${basePath}questionnaire/`;

  const questionnaireRequest = fetch(questionnairePath)
    .then((res) => res.json())
    .catch(() => []);
</script>

<main>
  {#await questionnaireRequest}
    Loading questionnaire...
  {:then questionnaire}
    <QuestionnaireObject {questionnaire} />
  {/await}
</main>
