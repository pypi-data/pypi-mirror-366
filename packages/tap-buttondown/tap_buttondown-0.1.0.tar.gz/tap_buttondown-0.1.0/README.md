# tap-buttondown

A [Singer](https://singer.io) tap for extracting data from the [Buttondown API](https://buttondown.email/api).

## Installation

```bash
pip install tap-buttondown
```

Or run directly with `uvx`.

```bash
uvx tap-buttondown --help

# Example with CSV target
uvx tap-buttondown --config config.json | uvx --with setuptools target-csv
```

## Configuration

Create a `config.json` file with your Buttondown API key:

```json
{
  "api_key": "your_buttondown_api_key_here"
}
```

You can find your API key in your [Buttondown dashboard](https://buttondown.email/settings/api).

## Usage

### Discover available streams

```bash
tap-buttondown --config config.json --discover
```

This will output a catalog of available streams in JSON format.

### Run the tap

```bash
tap-buttondown --config config.json --catalog catalog.json
```

Or to use the default catalog:

```bash
tap-buttondown --config config.json
```

### State management

To maintain state between runs (for incremental syncs):

```bash
tap-buttondown --config config.json --state state.json
```

## Streams

### Subscribers

The `subscribers` stream extracts subscriber data from your Buttondown newsletter.

**Schema:**
- `id` (string): Unique subscriber ID
- `email` (string): Subscriber email address
- `created_date` (datetime): When the subscriber was created
- `updated_date` (datetime): When the subscriber was last updated
- `metadata` (object): Custom metadata
- `notes` (string, nullable): Notes about the subscriber
- `preferences` (object): Subscriber preferences
- `subscription_preferences` (object): Subscription-specific preferences
- `tags` (array): Tags associated with the subscriber
- `source` (string, nullable): Source of the subscription
- `unsubscribed_date` (datetime, nullable): When the subscriber unsubscribed
- `referrer_url` (string, nullable): Referrer URL
- `utm_campaign` (string, nullable): UTM campaign parameter
- `utm_content` (string, nullable): UTM content parameter
- `utm_medium` (string, nullable): UTM medium parameter
- `utm_source` (string, nullable): UTM source parameter
- `utm_term` (string, nullable): UTM term parameter
- `gclid` (string, nullable): Google Click ID
- `fbc` (string, nullable): Facebook Click ID
- `fbp` (string, nullable): Facebook Browser ID
- `subscribed` (boolean): Whether the subscriber is currently subscribed
- `unsubscribed` (boolean): Whether the subscriber has unsubscribed

**Replication Method:** INCREMENTAL
**Replication Key:** `updated_date`

## Development

This project is managed with `uv`.

### Setup

1. Clone the repository
1. Create a `config.json` file with your API key

### Testing

```bash
# Discover streams
uv run tap-buttondown --config config.json --discover

# Run sync
uv run tap-buttondown --config config.json
```

## License

This project is licensed under the MIT License.
