let currentChatId = null;
let chatInitialized = false;
let currentDocumentName = null;


const API_URL =
    "https://ai-document-chatbot-deployment.onrender.com";


// ============================================
// DOM ELEMENTS
// ============================================

const fileInput =
    document.getElementById("file-input");


const uploadStatus =
    document.getElementById("upload-status");


const questionInput =
    document.getElementById("question-input");


const sendButton =
    document.getElementById("send-btn");


const chatContainer =
    document.getElementById("chat-container");


const newChatButton =
    document.querySelector(".new-chat-btn");


const historyList =
    document.getElementById("history-list");


// ============================================
// MOBILE SIDEBAR ELEMENTS
// ============================================

const mobileMenuButton =
    document.getElementById("mobile-menu-btn");


const mobileCloseButton =
    document.getElementById("mobile-close-btn");


const sidebar =
    document.querySelector(".sidebar");


const sidebarOverlay =
    document.getElementById("sidebar-overlay");


// ============================================
// MOBILE SIDEBAR FUNCTIONS
// ============================================

function openMobileSidebar() {

    sidebar.classList.add("open");

    sidebarOverlay.classList.add("open");

}


function closeMobileSidebar() {

    sidebar.classList.remove("open");

    sidebarOverlay.classList.remove("open");

}


// Open sidebar

mobileMenuButton.addEventListener(
    "click",
    openMobileSidebar
);


// Close sidebar using X

mobileCloseButton.addEventListener(
    "click",
    closeMobileSidebar
);


// Close sidebar by clicking outside

sidebarOverlay.addEventListener(
    "click",
    closeMobileSidebar
);


// ============================================
// SESSION STORAGE
// ============================================

function saveSession() {

    sessionStorage.setItem(
        "currentChatId",
        currentChatId || ""
    );

}


function getSavedChatId() {

    return sessionStorage.getItem(
        "currentChatId"
    );

}


function getChatSessions() {

    const sessions =
        sessionStorage.getItem(
            "chatSessions"
        );


    if (!sessions) {

        return [];

    }


    try {

        return JSON.parse(
            sessions
        );

    } catch (error) {

        console.error(
            "Failed to read chat sessions:",
            error
        );

        return [];

    }

}


function saveChatSessions(sessions) {

    sessionStorage.setItem(
        "chatSessions",
        JSON.stringify(sessions)
    );

}


// ============================================
// CREATE NEW CHAT
// ============================================

async function createNewChat() {

    try {

        const response =
            await fetch(
                `${API_URL}/new-chat`,
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.detail ||
                "Failed to create chat"
            );

        }


        currentChatId =
            result.chat_id;


        currentDocumentName =
            null;


        saveSession();


        console.log(
            "New chat created:",
            currentChatId
        );


        return currentChatId;


    } catch (error) {

        console.error(
            "New chat error:",
            error
        );


        alert(
            "Could not create a new chat."
        );


        return null;

    }

}


// ============================================
// GET CURRENT CHAT MESSAGES
// ============================================

function getCurrentMessages() {

    const messages = [];


    const messageElements =
        chatContainer.querySelectorAll(
            ".user-message, .ai-message"
        );


    messageElements.forEach(
        element => {

            if (
                element.classList.contains(
                    "user-message"
                )
            ) {

                messages.push({

                    type: "user",

                    message:
                        element.textContent

                });

            } else {

                const answerElement =
                    element.querySelector(
                        ".ai-answer"
                    );


                const answer =
                    answerElement
                        ? answerElement.textContent
                        : element.textContent;


                let sources = [];


                try {

                    sources =
                        JSON.parse(
                            element.dataset.sources ||
                            "[]"
                        );

                } catch (error) {

                    sources = [];

                }


                messages.push({

                    type: "ai",

                    message: answer,

                    sources: sources

                });

            }

        }
    );


    return messages;

}


// ============================================
// SAVE CURRENT CHAT
// ============================================

function saveCurrentChat() {

    if (!currentChatId) {

        return;

    }


    const messages =
        getCurrentMessages();


    if (messages.length === 0) {

        return;

    }


    const sessions =
        getChatSessions();


    const existingIndex =
        sessions.findIndex(
            chat =>
                chat.chat_id ===
                currentChatId
        );


    const firstUserMessage =
        messages.find(
            message =>
                message.type === "user"
        );


    let title =
        firstUserMessage
            ? firstUserMessage.message
            : "New Chat";


    if (title.length > 35) {

        title =
            title.substring(0, 35) +
            "...";

    }


    const chatData = {

        chat_id:
            currentChatId,

        title:
            title,

        document:
            currentDocumentName,

        messages:
            messages

    };


    if (existingIndex !== -1) {

        sessions[existingIndex] =
            chatData;

    } else {

        sessions.unshift(
            chatData
        );

    }


    saveChatSessions(
        sessions
    );


    renderHistory();

}


// ============================================
// RESTORE CHAT
// ============================================

function restoreChat(chatId) {

    const sessions =
        getChatSessions();


    const chat =
        sessions.find(
            item =>
                item.chat_id ===
                chatId
        );


    if (!chat) {

        return;

    }


    currentChatId =
        chat.chat_id;


    currentDocumentName =
        chat.document || null;


    saveSession();


    chatContainer.innerHTML =
        "";


    chat.messages.forEach(
        message => {

            addMessage(
                message.type,
                message.message,
                message.sources || []
            );

        }
    );


    if (
        chat.messages.length === 0
    ) {

        showWelcomeMessage();

    }


    if (currentDocumentName) {

        uploadStatus.textContent =
            `Document: ${currentDocumentName}`;

    } else {

        uploadStatus.textContent =
            "Supported: PDF, TXT, DOCX";

    }


    renderHistory();


    console.log(
        "Restored chat:",
        currentChatId
    );

}


// ============================================
// RENDER SIDEBAR
// ============================================

function renderHistory() {

    historyList.innerHTML =
        "";


    const sessions =
        getChatSessions();


    sessions.forEach(
        chat => {

            const historyItem =
                document.createElement(
                    "div"
                );


            historyItem.className =
                "history-item";


            if (
                chat.chat_id ===
                currentChatId
            ) {

                historyItem.classList.add(
                    "active"
                );

            }


            // Chat title

            const title =
                document.createElement(
                    "div"
                );


            title.className =
                "history-title";


            title.textContent =
                chat.title;


            historyItem.appendChild(
                title
            );


            // Document name

            if (chat.document) {

                const documentName =
                    document.createElement(
                        "div"
                    );


                documentName.className =
                    "history-document";


                documentName.textContent =
                    `📄 ${chat.document}`;


                historyItem.appendChild(
                    documentName
                );

            }


            // Restore chat

            historyItem.addEventListener(
                "click",
                function () {

                    saveCurrentChat();


                    restoreChat(
                        chat.chat_id
                    );


                    // Close mobile sidebar
                    closeMobileSidebar();

                }
            );


            historyList.appendChild(
                historyItem
            );

        }
    );

}


// ============================================
// WELCOME MESSAGE
// ============================================

function showWelcomeMessage() {

    chatContainer.innerHTML = `
        <div class="welcome-message">

            <h2>
                👋 Welcome!
            </h2>

            <p>
                Upload a document and ask me
                anything about it.
            </p>

        </div>
    `;

}


// ============================================
// ADD MESSAGE
// ============================================

function addMessage(
    type,
    message,
    sources = []
) {

    const messageDiv =
        document.createElement(
            "div"
        );


    // ========================================
    // USER MESSAGE
    // ========================================

    if (
        type === "user"
    ) {

        messageDiv.className =
            "user-message";


        messageDiv.textContent =
            message;

    }


    // ========================================
    // AI MESSAGE
    // ========================================

    else {

        messageDiv.className =
            "ai-message";


        // Store sources inside DOM

        messageDiv.dataset.sources =
            JSON.stringify(
                sources
            );


        const answerDiv =
            document.createElement(
                "div"
            );


        answerDiv.className =
            "ai-answer";


        answerDiv.textContent =
            message;


        messageDiv.appendChild(
            answerDiv
        );


        // ====================================
        // SOURCE DISPLAY
        // ====================================

        if (
            sources.length > 0
        ) {

            const sourceDiv =
                document.createElement(
                    "div"
                );


            sourceDiv.className =
                "source";


            const sourceTitle =
                document.createElement(
                    "strong"
                );


            sourceTitle.textContent =
                "Sources";


            sourceDiv.appendChild(
                sourceTitle
            );


            sources.forEach(
                source => {

                    const sourceItem =
                        document.createElement(
                            "div"
                        );


                    sourceItem.className =
                        "source-item";


                    sourceItem.textContent =
                        `${source.document} — ` +
                        `Page ${source.page}`;


                    sourceDiv.appendChild(
                        sourceItem
                    );

                }
            );


            messageDiv.appendChild(
                sourceDiv
            );

        }

    }


    chatContainer.appendChild(
        messageDiv
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}


// ============================================
// UPLOAD DOCUMENT
// ============================================

fileInput.addEventListener(
    "change",
    async function () {

        const file =
            fileInput.files[0];


        if (!file) {

            return;

        }


        if (!currentChatId) {

            currentChatId =
                await createNewChat();


            if (!currentChatId) {

                return;

            }

        }


        uploadStatus.textContent =
            `Uploading ${file.name}...`;


        const formData =
            new FormData();


        formData.append(
            "chat_id",
            currentChatId
        );


        formData.append(
            "file",
            file
        );


        try {

            const response =
                await fetch(
                    `${API_URL}/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const result =
                await response.json();


            if (!response.ok) {

                uploadStatus.textContent =
                    result.detail ||
                    "Upload failed.";


                return;

            }


            if (
                result.duplicate
            ) {

                uploadStatus.textContent =
                    `${file.name} already exists ` +
                    `in this chat.`;


                return;

            }


            // Remember document

            currentDocumentName =
                file.name;


            uploadStatus.textContent =
                `${file.name} uploaded successfully. ` +
                `${result.chunks_created} chunks created.`;


            console.log(
                "Document uploaded for chat:",
                currentChatId
            );


            // Update sidebar

            saveCurrentChat();


        } catch (error) {

            console.error(
                "Upload error:",
                error
            );


            uploadStatus.textContent =
                "Could not connect to the server.";

        }

    }
);


// ============================================
// SEND QUESTION
// ============================================

async function sendQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        return;

    }


    if (!currentChatId) {

        alert(
            "No active chat. " +
            "Please click New Chat."
        );


        return;

    }


    const welcomeMessage =
        document.querySelector(
            ".welcome-message"
        );


    if (welcomeMessage) {

        welcomeMessage.remove();

    }


    addMessage(
        "user",
        question
    );


    questionInput.value =
        "";


    sendButton.disabled =
        true;


    sendButton.textContent =
        "⏳";


    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        chat_id:
                            currentChatId

                    })
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            addMessage(
                "ai",

                result.detail ||
                "Something went wrong."
            );


            return;

        }


        addMessage(
            "ai",
            result.answer,
            result.sources || []
        );


        // Save messages + sources

        saveCurrentChat();


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        addMessage(
            "ai",
            "Could not connect to the server."
        );

    } finally {

        sendButton.disabled =
            false;


        sendButton.textContent =
            "➤";

    }

}


// ============================================
// NEW CHAT
// ============================================

newChatButton.addEventListener(
    "click",
    async function () {

        // Save old conversation

        saveCurrentChat();


        // Create new chat

        const newChatId =
            await createNewChat();


        if (!newChatId) {

            return;

        }


        showWelcomeMessage();


        questionInput.value =
            "";


        fileInput.value =
            "";


        uploadStatus.textContent =
            "Supported: PDF, TXT, DOCX";


        renderHistory();


        // Close mobile sidebar

        closeMobileSidebar();


        console.log(
            "Active chat changed:",
            currentChatId
        );

    }
);


// ============================================
// SEND BUTTON
// ============================================

sendButton.addEventListener(
    "click",
    sendQuestion
);


// ============================================
// ENTER KEY
// ============================================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();


            sendQuestion();

        }

    }
);


// ============================================
// INITIALIZE
// ============================================

window.addEventListener(
    "DOMContentLoaded",
    async function () {

        if (chatInitialized) {

            return;

        }


        chatInitialized =
            true;


        const savedChatId =
            getSavedChatId();


        if (savedChatId) {

            console.log(
                "Restoring existing session:",
                savedChatId
            );


            currentChatId =
                savedChatId;


            restoreChat(
                savedChatId
            );


        } else {

            console.log(
                "No existing session. " +
                "Creating new chat."
            );


            currentChatId =
                await createNewChat();


            if (currentChatId) {

                showWelcomeMessage();


                renderHistory();

            }

        }

    }
);