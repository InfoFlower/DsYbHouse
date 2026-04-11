create or replace view musicdisg as
SELECT distinct
        music.id AS music_id,
        music.title AS music_title,
        music.description AS music_description,
        music.url AS music_url,
        music.channelTitle AS music_channelTitle,
        music.playlistId AS music_playlistId,
        music.videoOwnerChannelTitle AS music_videoOwnerChannelTitle,
        music.videoOwnerChannelId AS music_videoOwnerChannelId,
        ds.etag, 
        ds.title, 
        ds.country, 
        ds.year, 
        ds.label,
        dm.id,
        dm.data_quality,
        dm.lowest_price,
        dm.num_for_sale,
        dm.genres,
        dm.styles,
        r.count,
        r.average
        --t.title AS track_title,
        --t.position,
        --t.type_ AS track_type,
        --t.duration
from music 
left join discogs ds ON music.etag = ds.etag
left JOIN discogs_main dm ON ds.id = dm.id_main
left JOIN rating r ON r.id_main = dm.id_main
--JOIN tracklist t ON t.id_main = dm.id_main
;