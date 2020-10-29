<script lang="ts">
  import SaveQuestionaire from "./SaveQuestionaire.svelte";

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
    <SaveQuestionaire {questionnaire} />
  {/await}
</main>
