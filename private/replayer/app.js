const http = require('http');
const fs = require('fs');
const path = require('path');

const SESSION_TIMEOUT_MS = 5 * 60 * 1000;
const CLEARING_INTERVAL_MS = 1 * 60 * 1000;

const RELATIVE_REPLAYS_FOLDER = 'replays'
const SERVER_VERSION = '1.82.156';
var metaData;
var sessions = [];

http.createServer(function (request, response) {
    const URL_GRADIENTS = request.url.split('/');

    if ((URL_GRADIENTS[1] === 'observer-mode') &&
        (URL_GRADIENTS[2] === 'rest') &&
        (URL_GRADIENTS[3] === 'consumer')) {
        var gameId;
        var platformId;
        var sessionId;
        var chunkOrKeyframeId;
        const KIND = URL_GRADIENTS[4];
        if (typeof (URL_GRADIENTS[5]) === "string") {
            PLATFORM_GRADIENTS = URL_GRADIENTS[5].split('-');
            gameId = URL_GRADIENTS[6];
            platformId = PLATFORM_GRADIENTS[0];
            sessionId = PLATFORM_GRADIENTS[1];
            chunkOrKeyframeId = URL_GRADIENTS[7];
        }
        console.log(KIND);
        switch (KIND) {
            case 'version':
                var contentType = 'text/plain';
                var content = SERVER_VERSION;
                break;
            case 'getGameMetaData':
                var contentType = 'application/json';
                var content = getGameMetaData(
                    platformId, gameId, sessionId);
                break;
            case 'getLastChunkInfo':
                var contentType = 'application/json';
                var content = getLastChunkInfo(
                    platformId, gameId, sessionId);
                break;
            case 'getGameDataChunk':
                var contentType = 'application/octet-stream';
                var content = getGameDataChunk(
                    platformId, gameId, chunkOrKeyframeId);
                break;
            case 'getKeyFrame':
                var contentType = 'application/octet-stream';
                var content = getKeyFrame(
                    platformId, gameId, chunkOrKeyframeId);
                break;
            case 'end':
                clearingSession(sessionId);
                var contentType = 'text/plain';
                var content = 'OK';
                break;
            default:
                break;
        }
        if (content) {
            response.writeHead(200, { 'Content-Type': contentType });
            if (contentType === 'application/octet-stream') {
                content.pipe(response);
            }
            else {
                response.end(content);
            }
        }
        else {
            responseError(response, request);
        }
    }
    else {
        responseError(response, request);
    }
}).listen(1337);
console.log('Server running at http://127.0.0.1:1337/');

function responseError(response, request) {
    console.log('couldn\'t handle url ' + request.url);
    response.writeHead(400);
    response.end();
}

function generatePath(kind, platformId, gameId, file) {
    return path.resolve(RELATIVE_REPLAYS_FOLDER, platformId, gameId, kind, file);
}

function getFileContent(filePath) {
    if (fs.existsSync(filePath)) {
        return fs.readFileSync(filePath, 'utf8');
    }
}

function getFileStream(filePath) {
    if (fs.existsSync(filePath)) {
        return fs.createReadStream(filePath);
    }
}

function getGameMetaData(platformId, gameId, sessionId) {
    console.log('new session: ' + sessionId);
    sessions[sessionId] = Date.now();
    //console.log('sessions:\r\n"' + sessions + '"');
    const FILE_PATH = generatePath('.',
        platformId, gameId, 'metas.json');
    metaData = JSON.parse(getFileContent(FILE_PATH));

    returnMetas = {
        gameKey: {
            gameId: gameId,
            platformId: platformId
        },
        gameServerAddress:'',
        port: 0,
        encryptionKey: '',
        chunkTimeInterval: 30000,
        gameEnded: false,
        lastChunkId: metaData.firstChunkId,
        lastKeyFrameId: 1,
        endStartupChunkId: metaData.endStartupChunkId,
        delayTime: 150000,
        startGameChunkId: metaData.startGameChunkId,
        keyFrameTimeInterval: 60000,
        endGameChunkId: -1,
        endGamekeyFrameId: -1,
        decodedEncryptionKey: "",
        featuredGame: false,
        gameLength: 0,
        clientAddedLag: 30000,
        clientBackFetchingEnabled: false,
        clientBackFetchingFreq: 1000
    };

    return JSON.stringify(returnMetas) ;
}

function getLastChunkInfo(platformId, gameId, sessionId) {
    if (!(sessionId in sessions)) {
        return;
    }
    var timeSinceMeta = Date.now() - sessions[sessionId];

    const START_TIME_MS = 30000;
    const FOLLOW_UP_DELAY = 15000;
    const FOLLOW_UP_TIME_MS = START_TIME_MS + FOLLOW_UP_DELAY;

    var info;

    console.log('timeSinceMeta: ' + timeSinceMeta);

    //keyFrameId: Math.floor(chunkId / 2);
    
    if (timeSinceMeta < START_TIME_MS) {
        // start condition
        var CHUNK_ID = metaData.endStartupChunkId + 1;
        info = {
            chunkId: CHUNK_ID,
            availableSince: timeSinceMeta,
            nextAvailableChunk: (30000 - timeSinceMeta),
            keyFrameId: Math.floor(CHUNK_ID / 2),
            nextChunkId: CHUNK_ID-1,
            endStartupChunkId: metaData.endStartupChunkId,
            startGameChunkId: metaData.startGameChunkId,
            endGameChunkId: 0,
            duration: 30000
        };
    }
    else if (timeSinceMeta < FOLLOW_UP_TIME_MS) {
        // followup condition
        const AVAILABLE_SINCE = timeSinceMeta - START_TIME_MS;
        var CHUNK_ID = metaData.startGameChunkId;
        info = {
            chunkId: CHUNK_ID,
            availableSince: AVAILABLE_SINCE,
            nextAvailableChunk: (FOLLOW_UP_DELAY - AVAILABLE_SINCE),
            keyFrameId: Math.floor(CHUNK_ID/2),
            nextChunkId: CHUNK_ID-1,
            endStartupChunkId: metaData.endStartupChunkId,
            startGameChunkId: metaData.startGameChunkId,
            endGameChunkId: 0,
            duration: 30000
        };
    } else {
        // end condition
        info = {
            chunkId: metaData.endGameChunkId,
            availableSince: 27000,
            nextAvailableChunk: 3000,
            keyFrameId: metaData.endGameKeyFrameId,
            nextChunkId: metaData.endGameChunkId-1,
            endStartupChunkId: metaData.endStartupChunkId,
            startGameChunkId: metaData.startGameChunkId,
            endGameChunkId: metaData.endGameChunkId,
            duration: 30000
        };
    }

    console.log(info);

    return JSON.stringify(info);
}

function getGameDataChunk(platformId, gameId, chunkId) {
    console.log('getGameDataChunk ' + chunkId);
    const FILE_PATH = generatePath('gameDataChunk',
        platformId, gameId, chunkId);
    return getFileStream(FILE_PATH);
}

function getKeyFrame(platformId, gameId, keyframeId) {
    console.log('getKeyFrame ' + keyframeId);
    const FILE_PATH = generatePath('keyFrame',
        platformId, gameId, keyframeId);
    return getFileStream(FILE_PATH);
}

function clearingSession(sessionId) {
    if (sessionId in sessions) {
        sessions.splice(sessions.indexOf(sessionId), 1);
    }
}

setInterval(() => {
    const NOW = Date.now();
    for (sessionId in sessions) {
        if ((NOW - sessions[sessionId]) > SESSION_TIMEOUT_MS) {
            clearingSession(sessionId);
        }
    }
}, CLEARING_INTERVAL_MS);
