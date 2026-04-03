CREATE TABLE IF NOT EXISTS "music" (
	"kind"	TEXT,
	"etag"	TEXT,
	"id"	TEXT,
	"publishedAt"	TEXT,
	"channelId"	TEXT,
	"title"	TEXT,
	"description"	TEXT,
	"url"	TEXT,
	"channelTitle"	TEXT,
	"playlistId"	TEXT,
	"position"	TEXT,
	"videoId"	TEXT,
	"videoOwnerChannelTitle"	TEXT,
	"videoOwnerChannelId"	TEXT,
	"Discogged"	TEXT,
	PRIMARY KEY("etag")
)