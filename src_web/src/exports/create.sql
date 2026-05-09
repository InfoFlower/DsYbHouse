CREATE TABLE "music" (
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
	"videoOwnerChannelId"	TEXT, Discogged TEXT,
	PRIMARY KEY("etag")
);

CREATE TABLE "discogs" (
	"Z_tech_index" TEXT,
	"country" TEXT,
	"year" TEXT,
	"format" TEXT,
	"label" TEXT,
	"type" TEXT,
	"genre" TEXT,
	"style" TEXT,
	"id" TEXT,
	"barcode" TEXT,
	"master_id" TEXT,
	"master_url" TEXT,
	"uri" TEXT,
	"catno" TEXT,
	"title" TEXT,
	"thumb" TEXT,
	"cover_image" TEXT,
	"resource_url" TEXT,
	"community" TEXT,
	"format_quantity" TEXT,
	"formats" TEXT,
	"etag" TEXT,
	PRIMARY KEY("id", "etag")
);

CREATE TABLE discogs_main (id_main TEXT, id TEXT, status TEXT, year TEXT, resource_url TEXT, uri TEXT, artists_sort TEXT, data_quality TEXT, format_quantity TEXT, date_added TEXT, date_changed TEXT, num_for_sale TEXT, lowest_price TEXT, title TEXT, country TEXT, released TEXT, released_formatted TEXT, genres TEXT, styles TEXT, thumb TEXT, estimated_weight TEXT, blocked_from_sale TEXT, is_offensive TEXT, "master_id" TEXT, "master_url" TEXT, "notes" TEXT);

CREATE TABLE artists ("id_main" TEXT, "name" TEXT, "anv" TEXT, "join" TEXT, "role" TEXT, "tracks" TEXT, "id" TEXT, "resource_url" TEXT, "thumbnail_url" TEXT);

CREATE TABLE labels ("id_main" TEXT, "name" TEXT, "catno" TEXT, "entity_type" TEXT, "entity_type_name" TEXT, "id" TEXT, "resource_url" TEXT, "thumbnail_url" TEXT);

CREATE TABLE companies ("id_main" TEXT, "name" TEXT, "catno" TEXT, "entity_type" TEXT, "entity_type_name" TEXT, "id" TEXT, "resource_url" TEXT, "thumbnail_url" TEXT);

CREATE TABLE formats ("id_main" TEXT, "name" TEXT, "qty" TEXT, "descriptions" TEXT, "text" TEXT);

CREATE TABLE community ("id_main" TEXT, "have" TEXT, "want" TEXT, "data_quality" TEXT, "status" TEXT);

CREATE TABLE rating ("id_main" TEXT, "count" TEXT, "average" TEXT);

CREATE TABLE submitter ("id_main" TEXT, "username" TEXT, "resource_url" TEXT);

CREATE TABLE contributors ("id_main" TEXT, "username" TEXT, "resource_url" TEXT);

CREATE TABLE videos ("id_main" TEXT, "uri" TEXT, "title" TEXT, "description" TEXT, "duration" TEXT, "embed" TEXT);

CREATE TABLE tracklist ("id_main" TEXT, "position" TEXT, "type_" TEXT, "title" TEXT, "duration" TEXT, "artists" TEXT, "extraartists" TEXT);

CREATE TABLE extraartists ("id_main" TEXT, "name" TEXT, "anv" TEXT, "join" TEXT, "role" TEXT, "tracks" TEXT, "id" TEXT, "resource_url" TEXT);

CREATE TABLE images ("id_main" TEXT, "type" TEXT, "uri" TEXT, "resource_url" TEXT, "uri150" TEXT, "width" TEXT, "height" TEXT);

CREATE TABLE identifiers ("id_main" TEXT, "type" TEXT, "value" TEXT, "description" TEXT);

CREATE TABLE series ("id_main" TEXT, "name" TEXT, "catno" TEXT, "entity_type" TEXT, "entity_type_name" TEXT, "id" TEXT, "resource_url" TEXT, "thumbnail_url" TEXT);

