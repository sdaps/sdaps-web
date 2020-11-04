<script lang="ts">
  import { updateKey } from "../keyTracker";

  // export interface ChoicegroupQuestionnaireObject extends OrderedObject {
  //   type: "choicegroup";
  //   heading: string;
  //   children: Array<InnerGroupAddChoice | InnerChoiceLine>;
  // }
  // export interface InnerGroupAddChoice extends OrderedObject {
  //   type: "groupaddchoice";
  //   choice: string;
  // }
  // export interface InnerChoiceLine extends OrderedObject {
  //   type: "choiceline";
  //   question: string;
  // }

  import {
    InputGroup,
    InputGroupAddon,
    InputGroupText,
    Input,
  } from "sveltestrap";

  import type {
    ChoicegroupQuestionnaireObject,
    InnerGroupAddChoice,
    InnerChoiceLine,
  } from "../questionnaire";
  import { getHighestKey } from "../questionnaire";

  export let choicegroup: ChoicegroupQuestionnaireObject;

  const key = getHighestKey(choicegroup.children);
  const listKey = updateKey(key);

  function createSubObject(type: "groupaddchoice"): InnerGroupAddChoice;
  function createSubObject(type: "choiceline"): InnerChoiceLine;
  function createSubObject(type) {
    if (type === "groupaddchoice") {
      return { id: $listKey, type, choice: "Choice" };
    } else if (type === "choiceline") {
      return { id: $listKey, type, question: "Question" };
    }
  }

  let mode: "groupaddchoice" | "choiceline" = "choiceline";

  // Add and remove
  function addSection(idx: number) {
    const startIdx = idx + 1;

    $listKey += 1;

    choicegroup.children.splice(startIdx, 0, createSubObject(mode));

    choicegroup.children = choicegroup.children;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    choicegroup.children.splice(startIdx, 1);

    choicegroup.children = choicegroup.children;
  }

  // Drag and drop

  const flipDurationMs = 50;

  function handleDndConsider(e) {
    choicegroup.children = e.detail.items;
  }

  function handleDndFinalize(e) {
    choicegroup.children = e.detail.items;
  }
</script>

<InputGroup>
  <InputGroupAddon addonType="prepend">
    <InputGroupText>Heading:</InputGroupText>
  </InputGroupAddon>
  <Input placeholder="heading" bind:value={choicegroup.heading} />
</InputGroup>

{#each choicegroup.children as child (child.id)}child{/each}
