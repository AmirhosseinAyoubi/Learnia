package com.learnia.document.repository;

import com.learnia.document.model.DocumentProcessingJob;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface DocumentProcessingJobRepository extends JpaRepository<DocumentProcessingJob, UUID> {
}