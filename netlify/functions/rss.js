const Parser = require('rss-parser');
const parser = new Parser();

exports.handler = async (event) => {
  try {
    const feedUrl = event.queryStringParameters.url;

    if (!feedUrl) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Missing RSS URL" }),
      };
    }

    const feed = await parser.parseURL(feedUrl);

    const items = feed.items.slice(0, 20).map(item => ({
      title: item.title,
      link: item.link,
      pubDate: item.pubDate,
      image:
        item.enclosure?.url ||
        item["media:content"]?.url ||
        null,
      description: item.contentSnippet || item.content || "",
    }));

    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(items),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};

