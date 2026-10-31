# DisplayHud

**Title:** DisplayHud

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Put your own information on the camera view's HUD, on top of the theme. `values` are variables for templates ({speed}, {task}); they are merged with earlier ones (send null to remove one). `blocks` are extra text blocks and `widgets` extra instruments, as in a HUD theme; each replaces the previous ones sent this way. `clear` removes everything added with this command. Kept until cleared, across HUD themes.

| Property               | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| ---------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#type )       | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )           | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )         | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#id )           | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                       |
| - [values](#values )   | No      | object  | No         | -          | -                                                            |
| - [blocks](#blocks )   | No      | array   | No         | -          | -                                                            |
| - [widgets](#widgets ) | No      | array   | No         | -          | -                                                            |
| - [clear](#clear )     | No      | boolean | No         | -          | -                                                            |

## <a name="type"></a>1. Property `Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

## <a name="ts"></a>2. Property `Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="seq"></a>3. Property `Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="id"></a>4. Property `Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="values"></a>5. Property `DisplayHud > values`

|                           |                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------- |
| **Type**                  | `object`                                                                            |
| **Required**              | No                                                                                  |
| **Additional properties** | [Each additional property must conform to the schema](#values_additionalProperties) |

| Property                            | Pattern | Type                            | Deprecated | Definition | Title/Description |
| ----------------------------------- | ------- | ------------------------------- | ---------- | ---------- | ----------------- |
| - [](#values_additionalProperties ) | No      | string, number, boolean or null | No         | -          | -                 |

### <a name="values_additionalProperties"></a>5.1. Property `DisplayHud > values > additionalProperties`

|              |                                   |
| ------------ | --------------------------------- |
| **Type**     | `string, number, boolean or null` |
| **Required** | No                                |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 80 |

## <a name="blocks"></a>6. Property `DisplayHud > blocks`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 8                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [block](#blocks_items)          | -           |

### <a name="blocks_items"></a>6.1. DisplayHud > blocks > block

|                           |                                 |
| ------------------------- | ------------------------------- |
| **Type**                  | `object`                        |
| **Required**              | No                              |
| **Additional properties** | Not allowed                     |
| **Defined in**            | ../hud.schema.json#/$defs/block |

| Property                              | Pattern | Type             | Deprecated | Definition       | Title/Description                                |
| ------------------------------------- | ------- | ---------------- | ---------- | ---------------- | ------------------------------------------------ |
| + [at](#blocks_items_at )             | No      | enum (of string) | No         | -                | -                                                |
| + [lines](#blocks_items_lines )       | No      | array of string  | No         | -                | -                                                |
| - [size](#blocks_items_size )         | No      | number           | No         | -                | Text size; 1 is about 4.5% of the screen height. |
| - [color](#blocks_items_color )       | No      | string           | No         | In #/$defs/color | -                                                |
| - [blink_ms](#blocks_items_blink_ms ) | No      | integer          | No         | -                | -                                                |

#### <a name="blocks_items_at"></a>6.1.1. Property `DisplayHud > blocks > blocks items > at`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "top-left"
* "top-right"
* "bottom-left"
* "bottom-right"
* "left"

#### <a name="blocks_items_lines"></a>6.1.2. Property `DisplayHud > blocks > blocks items > lines`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 16                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be          | Description |
| ---------------------------------------- | ----------- |
| [lines items](#blocks_items_lines_items) | -           |

##### <a name="blocks_items_lines_items"></a>6.1.2.1. DisplayHud > blocks > blocks items > lines > lines items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 80 |

#### <a name="blocks_items_size"></a>6.1.3. Property `DisplayHud > blocks > blocks items > size`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Text size; 1 is about 4.5% of the screen height.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 3 |

#### <a name="blocks_items_color"></a>6.1.4. Property `DisplayHud > blocks > blocks items > color`

|                |               |
| -------------- | ------------- |
| **Type**       | `string`      |
| **Required**   | No            |
| **Defined in** | #/$defs/color |

| Restrictions                      |                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^#[0-9a-fA-F]{6}$``` [Test](https://regex101.com/?regex=%5E%23%5B0-9a-fA-F%5D%7B6%7D%24) |

#### <a name="blocks_items_blink_ms"></a>6.1.5. Property `DisplayHud > blocks > blocks items > blink_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 0    |
| **Maximum**  | &le; 5000 |

## <a name="widgets"></a>7. Property `DisplayHud > widgets`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 6                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description                             |
| ------------------------------- | --------------------------------------- |
| [widget](#widgets_items)        | An instrument drawn from device values. |

### <a name="widgets_items"></a>7.1. DisplayHud > widgets > widget

|                           |                                  |
| ------------------------- | -------------------------------- |
| **Type**                  | `object`                         |
| **Required**              | No                               |
| **Additional properties** | Not allowed                      |
| **Defined in**            | ../hud.schema.json#/$defs/widget |

**Description:** An instrument drawn from device values.

| Property                       | Pattern | Type             | Deprecated | Definition | Title/Description                                                                                                |
| ------------------------------ | ------- | ---------------- | ---------- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| + [type](#widgets_items_type ) | No      | enum (of string) | No         | -          | \`compass\`: heading tape; \`horizon\`: artificial horizon from pitch and roll; \`battery\`: level and charging. |
| - [at](#widgets_items_at )     | No      | enum (of string) | No         | -          | Default: top for compass, center for horizon, top-right for battery.                                             |
| - [size](#widgets_items_size ) | No      | number           | No         | -          | -                                                                                                                |

#### <a name="widgets_items_type"></a>7.1.1. Property `DisplayHud > widgets > widgets items > type`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** `compass`: heading tape; `horizon`: artificial horizon from pitch and roll; `battery`: level and charging.

Must be one of:
* "compass"
* "horizon"
* "battery"

#### <a name="widgets_items_at"></a>7.1.2. Property `DisplayHud > widgets > widgets items > at`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default: top for compass, center for horizon, top-right for battery.

Must be one of:
* "top"
* "bottom"
* "center"
* "top-left"
* "top-right"
* "bottom-left"
* "bottom-right"

#### <a name="widgets_items_size"></a>7.1.3. Property `DisplayHud > widgets > widgets items > size`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | N/A    |
| **Maximum**  | &le; 3 |

## <a name="clear"></a>8. Property `DisplayHud > clear`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

----------------------------------------------------------------------------------------------------------------------------
