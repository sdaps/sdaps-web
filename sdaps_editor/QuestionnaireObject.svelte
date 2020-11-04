<script lang="ts">
  import { dndzone } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import { createQuestionnaireObject } from "./factory";
  import { updateKey } from "./keyTracker";

  import type { EditorQuestionnaire, MulticolChild } from "./questionnaire";
  import { getHighestKey } from "./questionnaire";

  import {
    ListGroupItem,
    Button,
    Col,
    Row,
    Badge,
    Card,
    CardBody,
  } from "sveltestrap";

  import Textbody from "./objects/Textbody.svelte";
  import Textbox from "./objects/Textbox.svelte";
  import Section from "./objects/Section.svelte";
  import Singlemark from "./objects/Singlemark.svelte";
  import Markgroup from "./objects/Markgroup.svelte";
  import Choicegroup from "./objects/Choicegroup.svelte";
  import Choicequestion from "./objects/Choicequestion.svelte";

  import LayoutMarker from "./LayoutMarker.svelte";

  export let questionnaire: EditorQuestionnaire;

  const stepCount = getHighestKey(questionnaire);
  const listKey = updateKey(stepCount);

  let tool: MulticolChild["type"] = "section";

  // Add and remove
  function addSection(idx: number, layout?: boolean) {
    const startIdx = idx + 1;

    $listKey += 1;

    if (layout) {
      questionnaire.splice(startIdx, 0, {
        id: $listKey,
        type: "LAYOUT",
        columns: 1,
      });
    } else {
      questionnaire.splice(
        startIdx,
        0,
        createQuestionnaireObject(tool, $listKey)
      );
    }

    questionnaire = questionnaire;
  }

  function deleteSection(idx: number) {
    const startIdx = idx;

    questionnaire.splice(startIdx, 1);

    questionnaire = questionnaire;
  }

  // Drag and drop

  const flipDurationMs = 50;

  function handleDndConsider(e) {
    questionnaire = e.detail.items;
  }

  function handleDndFinalize(e) {
    questionnaire = e.detail.items;
  }
</script>

<style>
  .sectionContainer {
    display: flex;
    flex-flow: column;

    width: 100%;
  }

  .moveSection {
    background-color: white;
  }

  .toolbox {
    display: block;
    position: sticky;
    top: 0;
    margin-bottom: 1em;
    z-index: 1;
  }

  .infoHeader {
    margin-bottom: 0.4em;
  }

  input[type="radio"] + label {
    color: white;
    line-height: normal;
  }

  input[type="radio"] {
    margin-top: -1px;
    vertical-align: middle;
  }
</style>

<main>
  <div class="toolbox">
    <Card color="dark">
      <CardBody>
        <Row>
          <Col>
            <input
              type="radio"
              id="section"
              name="tool"
              value="section"
              bind:group={tool} />
            <label for="section">Section</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="textbody"
              name="tool"
              value="textbody"
              bind:group={tool} />
            <label for="textbody">Textbody</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="textbox"
              name="tool"
              value="textbox"
              bind:group={tool} />
            <label for="textbox">Textbox</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="singlemark"
              name="tool"
              value="singlemark"
              bind:group={tool} />
            <label for="singlemark">Singlemark</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="markgroup"
              name="tool"
              value="markgroup"
              bind:group={tool} />
            <label for="markgroup">Markgroup</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="choicegroup"
              name="tool"
              value="choicegroup"
              bind:group={tool} />
            <label for="choicegroup">Choicegroup</label>
          </Col>
          <Col>
            <input
              type="radio"
              id="choicequestion"
              name="tool"
              value="choicequestion"
              bind:group={tool} />
            <label for="choicequestion">Choicequestion</label>
          </Col>
        </Row>
      </CardBody>
    </Card>
  </div>

  <div class="sectionContainer">
    <ListGroupItem>
      <Row>
        <Col>
          <Button
            size="sm"
            color="success"
            block
            outline
            on:click={() => addSection(-1)}>
            Add
            {tool}
          </Button>
        </Col>
        <Col>
          <Button
            on:click={() => addSection(-1, true)}
            size="sm"
            color="dark"
            outline
            block>
            Change layout
          </Button>
        </Col>
      </Row>
    </ListGroupItem>
    <div
      use:dndzone={{ items: questionnaire, flipDurationMs, dropTargetStyle: { outline: 'solid 2px blue' } }}
      on:consider={handleDndConsider}
      on:finalize={handleDndFinalize}>
      {#each questionnaire as questionnaireObject, idx (questionnaireObject.id)}
        <div class="moveSection" animate:flip={{ duration: flipDurationMs }}>
          <ListGroupItem>
            <div class="infoHeader d-flex w-100 justify-content-between">
              <h6>
                <Badge color="dark">{questionnaireObject.type}</Badge>
              </h6>
              <small>
                <Button
                  on:click={() => deleteSection(idx)}
                  color="danger"
                  size="sm">
                  Remove
                </Button>
              </small>
            </div>
            {#if questionnaireObject.type === 'textbody'}
              <Textbody bind:textbody={questionnaireObject} />
            {:else if questionnaireObject.type === 'textbox'}
              <Textbox bind:textbox={questionnaireObject} />
            {:else if questionnaireObject.type === 'section'}
              <Section bind:section={questionnaireObject} />
            {:else if questionnaireObject.type === 'singlemark'}
              <Singlemark bind:singlemark={questionnaireObject} />
            {:else if questionnaireObject.type === 'markgroup'}
              <Markgroup bind:markgroup={questionnaireObject} />
            {:else if questionnaireObject.type === 'choicegroup'}
              <Choicegroup bind:choicegroup={questionnaireObject} />
            {:else if questionnaireObject.type === 'choicequestion'}
              <Choicequestion bind:choicequestion={questionnaireObject} />
            {:else if questionnaireObject.type === 'LAYOUT'}
              <LayoutMarker bind:marker={questionnaireObject} />
            {/if}
          </ListGroupItem>

          <ListGroupItem>
            <Row>
              <Col>
                <Button
                  size="sm"
                  color="success"
                  block
                  outline
                  on:click={() => addSection(idx)}>
                  Add
                  {tool}
                </Button>
              </Col>
              <Col>
                <Button
                  on:click={() => addSection(idx, true)}
                  size="sm"
                  color="dark"
                  outline
                  block>
                  Change layout
                </Button>
              </Col>
            </Row>
          </ListGroupItem>
        </div>
      {/each}
    </div>
  </div>
</main>
