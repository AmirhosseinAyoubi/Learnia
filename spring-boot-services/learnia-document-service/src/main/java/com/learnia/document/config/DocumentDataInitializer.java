package com.learnia.document.config;

import com.learnia.document.model.Document;
import com.learnia.document.model.DocumentProcessingJob;
import com.learnia.document.model.ProcessingStatus;
import com.learnia.document.repository.DocumentProcessingJobRepository;
import com.learnia.document.repository.DocumentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDateTime;
import java.util.UUID;

@Configuration
public class DocumentDataInitializer {

    @Bean
    CommandLineRunner initDocumentData(
            DocumentRepository documentRepository,
            DocumentProcessingJobRepository jobRepository
    ) {
        return args -> {

            if (documentRepository.count() >= 8) {
                return;
            }

            Document doc1 = new Document();
            doc1.setTitle("Introduction to Databases");
            doc1.setFileName("intro_to_databases.pdf");
            doc1.setFileType("PDF");
            doc1.setFileSize(245760L);
            doc1.setFileUrl("/uploads/intro_to_databases.pdf");
            doc1.setUploadedBy(UUID.randomUUID());
            doc1.setWorkspaceId(UUID.randomUUID());
            doc1.setProcessingStatus(ProcessingStatus.COMPLETED);
            doc1.setProcessingError(null);
            doc1.setPageCount(12);

            Document doc2 = new Document();
            doc2.setTitle("Spring Boot Notes");
            doc2.setFileName("spring_boot_notes.pdf");
            doc2.setFileType("PDF");
            doc2.setFileSize(512000L);
            doc2.setFileUrl("/uploads/spring_boot_notes.pdf");
            doc2.setUploadedBy(UUID.randomUUID());
            doc2.setWorkspaceId(UUID.randomUUID());
            doc2.setProcessingStatus(ProcessingStatus.PROCESSING);
            doc2.setProcessingError(null);
            doc2.setPageCount(25);

            Document doc3 = new Document();
            doc3.setTitle("Machine Learning Basics");
            doc3.setFileName("ml_basics.pdf");
            doc3.setFileType("PDF");
            doc3.setFileSize(310000L);
            doc3.setFileUrl("/uploads/ml_basics.pdf");
            doc3.setUploadedBy(UUID.randomUUID());
            doc3.setWorkspaceId(UUID.randomUUID());
            doc3.setProcessingStatus(ProcessingStatus.PENDING);
            doc3.setProcessingError(null);
            doc3.setPageCount(30);

            Document doc4 = new Document();
            doc4.setTitle("Data Structures Guide");
            doc4.setFileName("data_structures.pdf");
            doc4.setFileType("PDF");
            doc4.setFileSize(200000L);
            doc4.setFileUrl("/uploads/data_structures.pdf");
            doc4.setUploadedBy(UUID.randomUUID());
            doc4.setWorkspaceId(UUID.randomUUID());
            doc4.setProcessingStatus(ProcessingStatus.COMPLETED);
            doc4.setProcessingError(null);
            doc4.setPageCount(18);

            Document doc5 = new Document();
            doc5.setTitle("Operating Systems Overview");
            doc5.setFileName("os_overview.pdf");
            doc5.setFileType("PDF");
            doc5.setFileSize(275000L);
            doc5.setFileUrl("/uploads/os_overview.pdf");
            doc5.setUploadedBy(UUID.randomUUID());
            doc5.setWorkspaceId(UUID.randomUUID());
            doc5.setProcessingStatus(ProcessingStatus.PROCESSING);
            doc5.setProcessingError(null);
            doc5.setPageCount(22);

            Document doc6 = new Document();
            doc6.setTitle("Distributed Systems Concepts");
            doc6.setFileName("distributed_systems.pdf");
            doc6.setFileType("PDF");
            doc6.setFileSize(420000L);
            doc6.setFileUrl("/uploads/distributed_systems.pdf");
            doc6.setUploadedBy(UUID.randomUUID());
            doc6.setWorkspaceId(UUID.randomUUID());
            doc6.setProcessingStatus(ProcessingStatus.PENDING);
            doc6.setProcessingError(null);
            doc6.setPageCount(28);

            Document doc7 = new Document();
            doc7.setTitle("Computer Networks");
            doc7.setFileName("computer_networks.pdf");
            doc7.setFileType("PDF");
            doc7.setFileSize(350000L);
            doc7.setFileUrl("/uploads/computer_networks.pdf");
            doc7.setUploadedBy(UUID.randomUUID());
            doc7.setWorkspaceId(UUID.randomUUID());
            doc7.setProcessingStatus(ProcessingStatus.COMPLETED);
            doc7.setProcessingError(null);
            doc7.setPageCount(20);

            Document doc8 = new Document();
            doc8.setTitle("Software Engineering Principles");
            doc8.setFileName("software_engineering.pdf");
            doc8.setFileType("PDF");
            doc8.setFileSize(290000L);
            doc8.setFileUrl("/uploads/software_engineering.pdf");
            doc8.setUploadedBy(UUID.randomUUID());
            doc8.setWorkspaceId(UUID.randomUUID());
            doc8.setProcessingStatus(ProcessingStatus.PROCESSING);
            doc8.setProcessingError(null);
            doc8.setPageCount(26);

            documentRepository.save(doc1);
            documentRepository.save(doc2);
            documentRepository.save(doc3);
            documentRepository.save(doc4);
            documentRepository.save(doc5);
            documentRepository.save(doc6);
            documentRepository.save(doc7);
            documentRepository.save(doc8);

            Document[] docs = {doc1, doc2, doc3, doc4, doc5, doc6, doc7, doc8};

            for (int i = 0; i < docs.length; i++) {
                DocumentProcessingJob job = new DocumentProcessingJob();
                job.setDocument(docs[i]);
                job.setStatus(docs[i].getProcessingStatus().name());
                job.setStartedAt(LocalDateTime.now().minusMinutes(15 - i));
                job.setCompletedAt(
                        docs[i].getProcessingStatus() == ProcessingStatus.COMPLETED
                                ? LocalDateTime.now().minusMinutes(5 - i)
                                : null
                );
                job.setErrorMessage(null);

                jobRepository.save(job);
            }
        };
    }
}