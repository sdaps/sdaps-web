<script lang="ts">
  import type { EditorLayoutMarker } from "./questionnaire";
  import { FormGroup, CustomInput, Input, Row, Col } from "sveltestrap";

  export let marker: EditorLayoutMarker;

  enum Mode {
    SingleColumn = "single",
    MultiColumn = "multi",
  }

  let mode: Mode = marker.columns > 1 ? Mode.MultiColumn : Mode.SingleColumn;

  let columns: 1 | 2 | 3 | 4 = marker.columns > 1 ? marker.columns : 2;

  $: marker.columns = mode === Mode.SingleColumn ? 1 : columns;
</script>

<Row>
  <Col>
    <FormGroup>
      <CustomInput
        type="select"
        id="exampleCustomSelect"
        name="customSelect"
        bind:value={mode}>
        <option value={Mode.SingleColumn}>Single column</option>
        <option value={Mode.MultiColumn}>Multi column</option>
      </CustomInput>
    </FormGroup>
  </Col>

  {#if mode === Mode.MultiColumn}
    <Col>
      <FormGroup>
        <Input
          type="number"
          name="number"
          id="exampleNumber"
          min="2"
          max="4"
          step="1"
          bind:value={columns} />
      </FormGroup>
    </Col>
  {/if}
</Row>
