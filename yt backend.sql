create database yt;
use yt;


CREATE TABLE channels (
    Channel_Id VARCHAR(50) PRIMARY KEY,
    Channel_Name VARCHAR(255) NOT NULL,
    Subscribers INT,
    Views INT,
    Total_Videos INT,
    Channel_Description TEXT,
    Playlist_Id VARCHAR(50)
);






CREATE TABLE videos (
    Video_Id VARCHAR(255) PRIMARY KEY,
    Channel_Name VARCHAR(255) NOT NULL,
    Channel_Id VARCHAR(255),
    Title VARCHAR(255) NOT NULL,
    Tags VARCHAR(255),
    Thumbnail VARCHAR(255),
    Description VARCHAR(255),
    Published_Date VARCHAR(255),
    Duration VARCHAR(255),
    Views VARCHAR(255),
    Likes VARCHAR(255),
    Comments VARCHAR(255),
    Favorite_Count VARCHAR(255),
    Definition VARCHAR(255),
    Caption_Status VARCHAR(255)
);




select * from channels;

select * from videos;


drop table  channels;

drop table video;


drop database yt;
ALTER TABLE videos MODIFY Views BIGINT;

