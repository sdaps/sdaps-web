<script lang="ts">
  import { writable } from "svelte/store";

  import QuestionnaireObject from "./QuestionnaireObject.svelte";
  import type { Questionnaire } from "./questionnaire";
  import { onDestroy } from "svelte";
  import throttle from "lodash/throttle";

  export let questionnaire: Questionnaire;

  const questionnaireStore = writable(questionnaire);

  const basePath = window.location.pathname;
  const questionnairePath = `${basePath}questionnaire/`;

  function getCookie(name) {
    if (!document.cookie) {
      return null;
    }

    const xsrfCookies = document.cookie
      .split(";")
      .map((c) => c.trim())
      .filter((c) => c.startsWith(name + "="));

    if (xsrfCookies.length === 0) {
      return null;
    }
    return decodeURIComponent(xsrfCookies[0].split("=")[1]);
  }

  function save(value: Questionnaire) {
    const csrfToken = getCookie("csrftoken");

    fetch(questionnairePath, {
      method: "POST",
      body: JSON.stringify(value),
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });
  }

  const unsubscribe = questionnaireStore.subscribe(
    throttle((value) => save(value), 2000, { leading: true })
  );

  onDestroy(unsubscribe);
</script>

<QuestionnaireObject bind:questionnaire={$questionnaireStore} />
