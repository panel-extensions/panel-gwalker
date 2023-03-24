import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import { GraphicWalker } from '@kanaries/graphic-walker';
import { html } from 'htm/react';
import * as ReactDOM from 'react-dom';

import {transform_cds_to_records} from "./data"
import {HTMLBox, HTMLBoxView} from "./layout"

export class GWalkerView extends HTMLBoxView {
  container: HTMLDivElement
  model: GWalker
  walker: any

  connect_signals(): void {
    super.connect_signals()
    const update = () => {
    }
    this.connect(this.model.source.properties.data.change, update)
  }

  _render_item(): any {
    var props = {...this.model.config, dataSource: transform_cds_to_records(this.model.source)}
    console.log(props)
    return html`<${GraphicWalker} ...${props}/>`
  }

  render(): void {
    super.render()
    const mid = `pyg-${this.model.id}`;
    this.container = div({id: mid, style: 'display: contents;'})
    ReactDOM.render(this._render_item(), this.container)
    this.shadow_el.append(this.container)
  }
}

export namespace GWalker {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    config: p.Property<any>
    source: p.Property<ColumnDataSource>
  }
}

export interface GWalker extends GWalker.Attrs {}

export class GWalker extends HTMLBox {
  properties: GWalker.Props

  constructor(attrs?: Partial<GWalker.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.graphic_walker"

  static {
    this.prototype.default_view = GWalkerView

    this.define<GWalker.Props>(({Any, Ref}) => ({
      config:      [ Any,                        ],
      source:      [ Ref(ColumnDataSource),      ],
    }))
  }
}
