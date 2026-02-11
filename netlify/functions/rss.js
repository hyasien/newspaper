exports.handler = async function () {
  const rssUrl = "https://rss.app/feeds/yourfeed.xml"; // ضع هنا رابط RSS الموثوق

  try {
    const response = await fetch(rssUrl);
    const data = await response.text();

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/xml",
        "Access-Control-Allow-Origin": "*"
      },
      body: data
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: "Error fetching RSS"
    };
  }
};
